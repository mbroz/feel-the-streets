from .address_aware import AddressAwareGenerator
from shared.entities import Building

class BuildingGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Building)
        self.unprefixes("building")
        self.renames("roof:height", "roof_height")
        self.renames("roof:shape", "roof_shape")
        self.renames("building:roof:shape", "roof_shape")
        self.renames("roof:type", "roof_shape")
        self.renames("building:roof:angle", "roof_angle")
        self.renames("roof:slope:angle", "roof_angle")
        self.renames("roof:orientation", "roof_orientation")
        self.renames("building:roof:orientation", "roof_orientation")
        self.renames("internet_access:fee", "internet_access_fee")
        self.renames("information", "information_type")
        self.renames("webpage", "website")
        self.renames("url", "website")
        self.renames("diet:vegetarian", "vegetarian_diet")
        self.renames("heritage:operator", "heritage_operator")
        self.renames("payment:visa", "visa_payment")
        self.renames("payment:visa_debit", "visa_debit_payment")
        self.renames("payment:visa_electron", "visa_electron_payment")
        self.renames("roof:levels", "roof_levels")
        self.renames("building:roof:levels", "roof_levels")
        self.renames("roof:material", "roof_material")
        self.renames("roof", "roof_shape")
        self.renames("building:roof", "roof_shape")
        self.renames("wheelchair:description", "wheelchair_description")
        self.renames("community_centre:for", "community_centre_for")
        self.renames("leisure", "leisure_type")
        self.renames("tourism", "tourism_type")
        self.renames("industrial", "industrial_type")
        self.renames("building:levels:underground", "underground_levels")
        self.renames("roof:angle", "roof_angle")
        self.renames("roof:colour", "roof_colour")
        self.renames("toilets:wheelchair", "wheelchair_toilets")
        self.renames("healthcare:speciality", "healthcare_speciality")
        # It should go out 
        self.renames("wheelchair:toilets", "wheelchair_toilets")
        self.renames("ph", "phone")
        self.renames("opening_hours:url", "opening_hours_url")

        self.unprefixes("contact")
        self.renames("historic", "historic_type")
        self.renames("id:čvut", "cvut_id")
        self.renames("description:en", "description_en")
        self.renames("internet_access:ssid", "internet_access_ssid")
        self.renames("payment:cash", "cash_payment")
        self.renames("note:en", "note_en")
        self.renames("payment:bitcoin", "bitcoin_payment")
        self.renames("toilets:disposal", "toilets_disposal")
        self.renames("payment:coins", "cash_payment")
        self.renames("payment:maestro", "maestro_payment")
        self.renames("payment:mastercard", "mastercard_payment")
        self.renames("payment:notes", "notes_payment")
        self.renames("diet:vegan", "vegan_diet")
        self.renames("payment:credit_cards", "credit_cards_payment")
        self.renames("payment:debit_cards", "debit_cards_payment")



        self.renames("roof:slope:direction", "roof_slope_direction")
        self.renames("roof:direction", "roof_direction")
        self.renames("bridge:support", "bridge_support")
        self.renames("diet:gluten_free", "gluten_free_diet")
        self.renames("man_made:disused", "disused_man_made")
        self.renames("part:vertical", "vertical_part")
        self.renames("seamark:type", "seamark_type")
        self.renames("diet:raw", "raw_diet")
        self.renames("wheelchair:description:en", "en_wheelchair_description")
        self.renames("payment:electronic_purses", "electronic_purses_payment")
        self.renames("garden:type", "garden_type")
        self.renames("payment:meal_voucher", "meal_voucher_payment")
        self.renames("currency:czk", "currency_czk")
        self.renames("payment:american_express", "american_express_payment")
        self.renames("payment:cryptocurrencies", "cryptocurrencies_payment")
        self.renames("access:roof", "roof_access")
        self.renames("payment:meal_vouchers", "meal_vouchers_payment")
    @staticmethod
    def accepts(props):
        return ("building" in props and "aerialway" not in props) or "shop" in props or "building:levels" in props or ("amenity" in props and props["amenity"] in {"kindergarten", "school", "college", "hospital", "restaurant", "doctors", "veterinary", "dentist", "clinic"}) or ("type" in props and props["type"] == "building")