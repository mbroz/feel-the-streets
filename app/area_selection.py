import wx
from .server_interaction import has_api_connectivity, get_areas, request_area_creation
from .time_utils import rfc_3339_to_local_string



def get_local_area_infos():
    results = []
    # Somewhat hacky, but we need the storage root only there and the path generation logic does not care whether the area actually exists.
    areas_storage_path = os.path.dirname(AreaDatabase.path_for("someplace"))
    for db_file in glob.glob(os.path.join(areas_storage_path, "*.db")):
        name = os.path.basename(db_file).replace(".db", "")
        mtime = os.path.getmtime(db_file)
        results.append({"name":name, "updated_at": mtime, "state": "local"})
    return results


class AreaSelectionDialog(wx.Dialog):
    xrc_name = "area_selection"

    def post_init(self):
        self.Raise()
        self._areas = self.FindWindowByName("areas")
        if has_api_connectivity():
            available = get_areas()
        else:
            available = get_local_area_infos()
            self.FindWindowByName("request").Disable()
        self._area_names = [a["name"] for a in available]
        self._fill_areas(available)

    def _fill_areas(self, areas):
        for area in areas:
            area["created_at"] = rfc_3339_to_local_string(area["created_at"])
            area["updated_at"] = rfc_3339_to_local_string(area["updated_at"])
            self._areas.Append(_("{name}: {state}, last updated {updated_at}, created {created_at}").format(**area))
    
    @property
    def selected_map(self):
        return self._area_names[self._areas.Selection]
    
    def on_request_clicked(self, evt):
        name = wx.GetTextFromUser(_("Enter the name of the requested area"), _("Area name requested"))
        if not name:
            return
        reply = request_area_creation(name)
        if reply and isinstance(reply, dict) and "state" in reply and reply["state"] == "Creating":
            wx.MessageBox(_("The area creation request has been sent successfully. The area will become updated in a few minutes."), _("Success"), style=wx.ICON_INFORMATION)
        else:
            wx.MessageBox(_("The area creation request failed. Response from server: {reply}").format(reply=reply), _("Failure"), style=wx.ICON_ERROR)