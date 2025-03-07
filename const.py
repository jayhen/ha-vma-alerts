"""Constants for the Swedish VMA Alerts integration."""

DOMAIN = "vma_alerts"
PLATFORMS = ["sensor", "binary_sensor"]

# API details
API_ENDPOINT = "https://vmaapi.sr.se/api/v2/alerts"
TEST_API_ENDPOINT = "https://vmaapi.sr.se/testapi/v2/examples/data"
API_ENDPOINT_SWAGGER = "https://vmaapi.sr.se/swagger/v2.0/swagger.json"

# Configuration
CONF_GEOCODE = "geocode"
CONF_GEOCODES = "geocodes"
CONF_LANGUAGE = "language"
CONF_SHOW_EXPIRED = "show_expired"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_USE_TEST_API = "use_test_api"

# Default values
DEFAULT_LANGUAGE = "sv-SE"
DEFAULT_SHOW_EXPIRED = False
DEFAULT_NAME = "VMA Alerts"
DEFAULT_USE_TEST_API = False
SCAN_INTERVAL = 60  # seconds

# Alert statuses
STATUS_ACTUAL = "Actual"
STATUS_EXERCISE = "Exercise"
STATUS_TEST = "Test"

# Alert message types
MESSAGE_TYPE_ALERT = "Alert"
MESSAGE_TYPE_UPDATE = "Update"
MESSAGE_TYPE_CANCEL = "Cancel"

# Alert severities
SEVERITY_EXTREME = "Extreme"
SEVERITY_SEVERE = "Severe"
SEVERITY_MODERATE = "Moderate"
SEVERITY_MINOR = "Minor"
SEVERITY_UNKNOWN = "Unknown"

# Alert urgencies
URGENCY_IMMEDIATE = "Immediate"
URGENCY_EXPECTED = "Expected"
URGENCY_FUTURE = "Future"
URGENCY_PAST = "Past"
URGENCY_UNKNOWN = "Unknown"

# Alert certainties
CERTAINTY_OBSERVED = "Observed"
CERTAINTY_LIKELY = "Likely"
CERTAINTY_POSSIBLE = "Possible"
CERTAINTY_UNLIKELY = "Unlikely"
CERTAINTY_UNKNOWN = "Unknown"

# Attributes
ATTR_HEADLINE = "headline"
ATTR_DESCRIPTION = "description"
ATTR_INSTRUCTION = "instruction"
ATTR_AREA = "area"
ATTR_SENT = "sent"
ATTR_EFFECTIVE = "effective"
ATTR_EXPIRES = "expires"
ATTR_STATUS = "status"
ATTR_MESSAGE_TYPE = "message_type"
ATTR_SEVERITY = "severity"
ATTR_URGENCY = "urgency"
ATTR_CERTAINTY = "certainty"
ATTR_EVENT = "event"
ATTR_SENDER_NAME = "sender_name"
ATTR_WEB = "web"
ATTR_CONTACT = "contact"
ATTR_PARAMETERS = "parameters"

# Swedish counties (län) and municipalities (kommuner) with codes
COUNTIES = {
    # Counties (län)
    "01": "Stockholms län",
    "03": "Uppsala län",
    "04": "Södermanlands län",
    "05": "Östergötlands län",
    "06": "Jönköpings län",
    "07": "Kronobergs län",
    "08": "Kalmar län",
    "09": "Gotlands län",
    "10": "Blekinge län",
    "12": "Skåne län",
    "13": "Hallands län",
    "14": "Västra Götalands län",
    "17": "Värmlands län",
    "18": "Örebro län",
    "19": "Västmanlands län",
    "20": "Dalarnas län",
    "21": "Gävleborgs län",
    "22": "Västernorrlands län",
    "23": "Jämtlands län",
    "24": "Västerbottens län",
    "25": "Norrbottens län",
    
    # Municipalities (kommuner) - Stockholm County
    "0114": "Upplands Väsby (Stockholm)",
    "0115": "Vallentuna (Stockholm)",
    "0117": "Österåker (Stockholm)",
    "0120": "Värmdö (Stockholm)",
    "0123": "Järfälla (Stockholm)",
    "0125": "Ekerö (Stockholm)",
    "0126": "Huddinge (Stockholm)",
    "0127": "Botkyrka (Stockholm)",
    "0128": "Salem (Stockholm)",
    "0136": "Haninge (Stockholm)",
    "0138": "Tyresö (Stockholm)",
    "0139": "Upplands-Bro (Stockholm)",
    "0140": "Nykvarn (Stockholm)",
    "0160": "Täby (Stockholm)",
    "0162": "Danderyd (Stockholm)",
    "0163": "Sollentuna (Stockholm)",
    "0180": "Stockholm (Stockholm)",
    "0181": "Södertälje (Stockholm)",
    "0182": "Nacka (Stockholm)",
    "0183": "Sundbyberg (Stockholm)",
    "0184": "Solna (Stockholm)",
    "0186": "Lidingö (Stockholm)",
    "0187": "Vaxholm (Stockholm)",
    "0188": "Norrtälje (Stockholm)",
    "0191": "Sigtuna (Stockholm)",
    "0192": "Nynäshamn (Stockholm)",
    
    # Municipalities (kommuner) - Skåne County
    "1214": "Svalöv (Skåne)",
    "1230": "Staffanstorp (Skåne)",
    "1231": "Burlöv (Skåne)",
    "1233": "Vellinge (Skåne)",
    "1256": "Östra Göinge (Skåne)",
    "1257": "Örkelljunga (Skåne)",
    "1260": "Bjuv (Skåne)",
    "1261": "Kävlinge (Skåne)",
    "1262": "Lomma (Skåne)",
    "1263": "Svedala (Skåne)",
    "1264": "Skurup (Skåne)",
    "1265": "Sjöbo (Skåne)",
    "1266": "Hörby (Skåne)",
    "1267": "Höör (Skåne)",
    "1270": "Tomelilla (Skåne)",
    "1272": "Bromölla (Skåne)",
    "1273": "Osby (Skåne)",
    "1275": "Perstorp (Skåne)",
    "1276": "Klippan (Skåne)",
    "1277": "Åstorp (Skåne)",
    "1278": "Båstad (Skåne)",
    "1280": "Malmö (Skåne)",
    "1281": "Lund (Skåne)",
    "1282": "Landskrona (Skåne)",
    "1283": "Helsingborg (Skåne)",
    "1284": "Höganäs (Skåne)",
    "1285": "Eslöv (Skåne)",
    "1286": "Ystad (Skåne)",
    "1287": "Trelleborg (Skåne)",
    "1290": "Kristianstad (Skåne)",
    "1291": "Simrishamn (Skåne)",
    "1292": "Ängelholm (Skåne)",
    "1293": "Hässleholm (Skåne)",
    
    # Municipalities (kommuner) - Västra Götaland County
    "1401": "Härryda (Västra Götaland)",
    "1402": "Partille (Västra Götaland)",
    "1407": "Öckerö (Västra Götaland)",
    "1415": "Stenungsund (Västra Götaland)",
    "1419": "Tjörn (Västra Götaland)",
    "1421": "Orust (Västra Götaland)",
    "1427": "Sotenäs (Västra Götaland)",
    "1430": "Munkedal (Västra Götaland)",
    "1435": "Tanum (Västra Götaland)",
    "1438": "Dals-Ed (Västra Götaland)",
    "1439": "Färgelanda (Västra Götaland)",
    "1440": "Ale (Västra Götaland)",
    "1441": "Lerum (Västra Götaland)",
    "1442": "Vårgårda (Västra Götaland)",
    "1443": "Bollebygd (Västra Götaland)",
    "1444": "Grästorp (Västra Götaland)",
    "1445": "Essunga (Västra Götaland)",
    "1446": "Karlsborg (Västra Götaland)",
    "1447": "Gullspång (Västra Götaland)",
    "1452": "Tranemo (Västra Götaland)",
    "1460": "Bengtsfors (Västra Götaland)",
    "1461": "Mellerud (Västra Götaland)",
    "1462": "Lilla Edet (Västra Götaland)",
    "1463": "Mark (Västra Götaland)",
    "1465": "Svenljunga (Västra Götaland)",
    "1466": "Herrljunga (Västra Götaland)",
    "1470": "Vara (Västra Götaland)",
    "1471": "Götene (Västra Götaland)",
    "1472": "Tibro (Västra Götaland)",
    "1473": "Töreboda (Västra Götaland)",
    "1480": "Göteborg (Västra Götaland)",
    "1481": "Mölndal (Västra Götaland)",
    "1482": "Kungälv (Västra Götaland)",
    "1484": "Lysekil (Västra Götaland)",
    "1485": "Uddevalla (Västra Götaland)",
    "1486": "Strömstad (Västra Götaland)",
    "1487": "Vänersborg (Västra Götaland)",
    "1488": "Trollhättan (Västra Götaland)",
    "1489": "Alingsås (Västra Götaland)",
    "1490": "Borås (Västra Götaland)",
    "1491": "Ulricehamn (Västra Götaland)",
    "1492": "Åmål (Västra Götaland)",
    "1493": "Mariestad (Västra Götaland)",
    "1494": "Lidköping (Västra Götaland)",
    "1495": "Skara (Västra Götaland)",
    "1496": "Skövde (Västra Götaland)",
    "1497": "Hjo (Västra Götaland)",
    "1498": "Tidaholm (Västra Götaland)",
    "1499": "Falköping (Västra Götaland)",
} 