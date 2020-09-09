from PySide2.QtWidgets import QInputDialog, QMessageBox, QApplication
from pygeodesy.ellipsoidalVincenty import LatLon
from ..humanization_utils import describe_entity, format_number
from ..services import speech, map, config
from ..objects_browser import ObjectsBrowserWindow
from ..road_segments_browser import RoadSegmentsBrowserDialog
from ..geometry_utils import get_road_section_angle, distance_filter, distance_between, get_meaningful_turns
from ..search import get_query_from_user, QueryExecutor, SearchIndicator
from ..services import menu_service
from ..menu_service import menu_command
from .interesting_entities_controller import interesting_entity_in_range
from .sound_controller import leave_disallowed_sound_played

class InteractivePersonController: 
    def __init__(self, person, main_window):
        self._person = person
        self._main_window = main_window
        self._browser_window = None
        self._search_progress = None
        self._search_executor = None
        menu_service().register_menu_commands(self)
        menu_service().menu_item_with_name("toggle_disallow_leave_roads").setChecked(config().navigation.disallow_leaving_roads)
        menu_service().menu_item_with_name("toggle_play_sounds_for_interesting_objects").setChecked(config().presentation.play_sounds_for_interesting_objects)
        menu_service().menu_item_with_name("toggle_announce_interesting_objects").setChecked(config().presentation.announce_interesting_objects)
        menu_service().menu_item_with_name("toggle_correct_direction").setChecked(config().navigation.correct_direction_after_leave_disallowed)
        leave_disallowed_sound_played.connect(self._leave_disalloved_sound_played)

    def _get_current_coordinates_string(self):
        lat = format_number(self._person.position.lat, config().presentation.coordinate_decimal_places)
        lon = format_number(self._person.position.lon, config().presentation.coordinate_decimal_places)
        return _("Longitude: {longitude}, latitude: {latitude}.").format(longitude=lon, latitude=lat)

    @menu_command(_("Information"), _("Current coordinates"), "c")
    def do_current_coords(self, evt):
        speech().speak(self._get_current_coordinates_string())

    @menu_command(_("Information"), _("Copy current coordinates"), "ctrl+c")
    def copy_current_coordinates(self, evt):
        QApplication.clipboard().setText(self._get_current_coordinates_string())
        speech().speak(_("Copied."))

    def _position_impl(self, objects):    
        if objects:
            for obj in objects:
                speech().speak(describe_entity(obj))
        else:
            speech().speak(_("Not known."))
    
    @menu_command(_("Information"), _("Position"), "l")
    def do_position(self, evt):
        self._position_impl(self._person.is_inside_of)
    
    @menu_command(_("Information"), _("Position - all objects, may be slow"), "ctrl+l")
    def do_position_slow(self, evt):
        self._position_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _position_detailed_impl(self, objects):
        window = ObjectsBrowserWindow(self._main_window, title=_("Current position"), unsorted_objects=self._person.is_inside_of, person=self._person)
        window.show()
        self._browser_window = window
    
    @menu_command(_("Information"), _("Detailed current position"), "shift+l")
    def position_detailed(self, evt):
        self._position_detailed_impl(self._person.is_inside_of)

    @menu_command(_("Information"), _("Detailed current position - all objects, may be slow"), "ctrl+shift+l")
    def do_position_detailed_slow(self, evt):
        self._position_detailed_impl(map().intersections_at_position(self._person.position, fast=False))
    
    def _nearest_impl(self, objects):
        if not objects:
            speech().speak(_("Nothing."))
            return
        self._browser_window = ObjectsBrowserWindow(self._main_window, title=_("Near by objects"), person=self._person, unsorted_objects=objects)
        self._browser_window.show()

    @menu_command(_("Information"), _("Nearest"), "n")
    def do_nearest(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, config().presentation.near_by_radius))

    @menu_command(_("Information"), _("Nearest - all objects, may be slow"), "ctrl+n")
    def do_nearest_slow(self, evt):
        self._nearest_impl(self._person.map.within_distance(self._person.position, config().presentation.near_by_radius, fast=False))
    
    @menu_command(_("Movement"), _("Step forward"), "up")
    def do_forward(self, evt):
        self._person.step_forward() 

    @menu_command(_("Movement"), _("Step backward"), "down")
    def do_backward(self, evt):
        self._person.step_backward() 
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the right"), "right")
    def turn_right(self, evt):
        self._person.rotate(5)
    
    @menu_command(_("Movement"), _("Turn 5 degrees to the left"), "left")
    def turn_left(self, evt):
        self._person.rotate(-5)
    
    @menu_command(_("Information"), _("Current direction"), "r")
    def do_current_rotation(self, evt):
        speech().speak(_("{degrees} degrees").format(degrees=format_number(self._person.direction, config().presentation.angle_decimal_places)))
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the right"), "ctrl+right")
    def turn_right90(self, evt):
        self._person.rotate(90)
    
    @menu_command(_("Movement"), _("Turn 90 degrees to the left"), "ctrl+left")
    def turn_left90(self, evt):
        self._person.rotate(-90)
    
    @menu_command(_("Movement"), _("Coordinate jump..."), "j")
    def do_jump(self, evt):
        x, ok = QInputDialog.getDouble(self._main_window, _("Coordinate"), _("Enter the longitude"), decimals=6, minValue=-180, maxValue=180)
        if not ok:
            return
        y, ok = QInputDialog.getDouble(self._main_window, _("Coordinate"), _("Enter the latitude"), decimals=6, minValue=-90, maxValue=90)
        if not ok:
            return
        self._person.move_to(LatLon(y, x))

    @menu_command(_("Information"), _("Current road section angle"), "o")
    def current_road_section_angle(self, evt):
        seen_road = False
        for obj in self._person.is_inside_of:
            if obj.is_road_like and not obj.value_of_field("area"):
                seen_road = True
                angle = get_road_section_angle(self._person, obj)
                angle = format_number(angle, config().presentation.angle_decimal_places)
                speech().speak(_("{road}: {angle}°").format(road=describe_entity(obj), angle=angle))
        if not seen_road:
            speech().speak(_("You are not on a road."))

    @menu_command(_("Information"), _("Road details"), "ctrl+o")
    def road_details(self, evt):
        road = self._maybe_select_road()
        if not road or road.value_of_field("area"):
            return
        dlg = RoadSegmentsBrowserDialog(self._main_window, person=self._person, road=road)
        dlg.exec_()

    @menu_command(_("Movement"), _("Turn according to a road"), "shift+o")
    def rotate_to_road(self, evt):
        road = self._maybe_select_road()
        if not road:
            return
        rot = get_road_section_angle(self._person, road)
        self._person.set_direction(rot)

    @menu_command(_("Movement"), _("Turn about..."), "Ctrl+r")
    def rotate_by(self, evt):
        amount, ok = QInputDialog.getDouble(self._main_window, _("Data"), _("Enter the angle"), minValue=-360, maxValue=360)
        if not ok:
            return
        self._person.rotate(float(amount))
    
    def _maybe_select_road(self):
        roads = [r for r in self._person.is_inside_of if r.is_road_like]
        if not roads:
            speech().speak(_("You are not on a road."))
            return None
        if len(roads) == 1:
            return roads[0]
        else:
            road_reprs = [describe_entity(r) for r in roads]
            road_repr, ok = QInputDialog.getItem(self._main_window, _("Request"), _("Select the road which should be the target of the operation"), road_reprs, editable=False)
            if not ok:
                return None
            return roads[road_reprs.index(road_repr)]
            
    @menu_command(_("Information"), _("Search..."), "ctrl+f")
    def do_search(self, evt):
        query, distance = get_query_from_user(self._main_window)
        self._search_executor = QueryExecutor(query, self._person.position, distance)
        self._search_executor.results_ready.connect(self._search_results_ready)
        self._search_executor.start()
        self._search_progress = SearchIndicator(self._main_window)
        #self._search_progress.show()
        speech().speak(_("Searching, please wait."))

    def _search_results_ready(self, results):
        if results:
            browser = ObjectsBrowserWindow(self._main_window, title=_("Search results"), unsorted_objects=results, person=self._person)
            self._search_progress.hide()
            browser.show()
            self._browser_window = browser
        else:
            self._search_progres.hide()
            QMessageBox.information(self._main_window, _("Information"), _("No object matches the given search criteria."))
    
    @menu_command(_("Bookmarks"), _("Add bookmark..."), "ctrl+b")
    def add_bookmark(self, evt):
        name, ok = QInputDialog.getText(self._main_window, _("Data entry"), _("Enter a name for the new bookmark"),)
        if not ok or not name:
            return
        self._person.map.add_bookmark(name, lon=self._person.position.lon, lat=self._person.position.lat)
    
    @menu_command(_("Bookmarks"), _("Go to bookmark..."), "b")
    def go_to_bookmark(self, evt):
        bookmarks = list(self._person.map.bookmarks)
        names = [b.name for b in bookmarks]
        name, ok = QInputDialog.getItem(self._main_window, _("Data entry"), _("Select a bookmark"), names, editable=False)
        if not ok:
            return
        bookmark = bookmarks[names.index(name)]
        self._person.move_to(LatLon(bookmark.latitude, bookmark.longitude))

    @menu_command(_("Bookmarks"), _("Remove bookmark..."), "ctrl+shift+b")
    def remove_bookmark(self, evt):
        bookmarks = list(self._person.map.bookmarks)
        reprs = [_("{name}: longitude: {longitude}, latitude: {latitude}").format(name=b.name, longitude=b.longitude, latitude=b.latitude) for b in bookmarks]
        repr, ok = QInputDialog.getItem(self._main_window, _("Data entry"), _("Select a bookmark"), reprs, editable=False)
        if not ok:
            return
        bookmark = bookmarks[reprs.index(repr)]
        if QMessageBox.question(self._main_window, _("Question"), _("Do you really want to delete the bookmark {name}?").format(name=bookmark.name)) == QMessageBox.Yes:
            map().remove_bookmark(bookmark)

    @menu_command(_("Options"), _("Disallow leaving roads"), "alt+o", checkable=True, name="toggle_disallow_leave_roads")
    def disallow_leaving_roads(self, checked):
        config().navigation.disallow_leaving_roads = bool(checked)
        config().save_to_user_config()

    @menu_command(_("Options"), _("Announce interesting objects"), checkable=True, name="toggle_announce_interesting_objects")
    def announce_interesting_objects(self, checked):
        config().presentation.announce_interesting_objects = bool(checked)
        config().save_to_user_config()

    @menu_command(_("Options"), _("Play sounds for interesting objects"), checkable=True, name="toggle_play_sounds_for_interesting_objects")
    def play_sounds_for_interesting_objects(self, checked):
        config().presentation.play_sounds_for_interesting_objects = bool(checked)
        config().save_to_user_config()

    def _go_looking_for_interesting(self, movement_fn):
        found_interesting = False
        initial_position = self._person.position
        def on_interesting(sender, entity):
            nonlocal found_interesting
            found_interesting = True
        interesting_entity_in_range.connect(on_interesting)
        while not found_interesting:
            movement_fn()
        distance = distance_between(initial_position, self._person.position)
        speech().speak(_("Interesting object found after {} meters.").format(format_number(distance, config().presentation.distance_decimal_places)))
    @menu_command(_("Movement"), _("Go forward looking for an interesting object"), "ctrl+up")
    def do_forward_until_no_interesting(self, evt):
        self._go_looking_for_interesting(self._person.step_forward)

    @menu_command(_("Movement"), _("Go backward looking for an interesting object"), "ctrl+down")
    def do_backward_until_no_interesting(self, evt):
        self._go_looking_for_interesting(self._person.step_backward)

    @menu_command(_("Movement"), _("Turn to a new road"), "t")
    def _turn_to_a_new_road(self, evt):
        roads = [r for r in self._person.is_inside_of if r.is_road_like]
        if not roads:
            speech().speak(_("There is no meaningful turn to perform, you are not on a road."))
            return
        # Assume that the last road is the one the user wants to turn to.
        new_road = roads[-1]
        turns = get_meaningful_turns(new_road, self._person)
        print(turns[0][2])
        if not turns:
            speech().speak(_("There is no meaningful turn to perform, the new road is too short."))
        elif len(turns) == 1:
            self._person.rotate(turns[0][2])
            speech().speak(_("Done."))
        else:
            angles_mapping = {turn[0]: turn[2] for turn in turns}
            angle_choices = list(angles_mapping.keys())
            angle_desc, ok = QInputDialog.getItem(self._main_window, _("Request"), _("Which turn you want to perform?"), angle_choices, editable=False)
            if not ok: return
            self._person.rotate(angles_mapping[angle_desc])
            speech().speak(_("Done."))


    def _leave_disalloved_sound_played(self, sender, because_of):
        if not config().navigation.correct_direction_after_leave_disallowed: return
        last_road = [r for r in because_of.is_inside_of if r.is_road_like][0]
        turn_choices = get_meaningful_turns(last_road, because_of)
        smaller = min(turn_choices, key=lambda i: i[2])
        speech().speak(_("Because of you settings, you will be turned {}").format(smaller[0]))
        because_of.rotate(smaller[2])

        
    @menu_command(_("Options"), _("Automatically correct your direction when attempting to exit the last road"), checkable=True, name="toggle_correct_direction")
    def toggle_correct_direction(self, checked):
        config().navigation.correct_direction_after_leave_disallowed = int(checked)
        config().save_to_user_config()