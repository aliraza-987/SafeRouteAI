import sqlite3
from datetime import datetime, timedelta
import random

DB_PATH = "saferoute.db"

INCIDENTS = [
    # ════════════════════════════════════════════
    # MUMBAI
    # ════════════════════════════════════════════

    # ── Aarey Colony / Goregaon ──────────────────
    (19.1590, 72.8777, "poor_lighting",  "Aarey Colony completely deserted after 9pm. No street lights on internal roads.", "late_night", "Aarey Colony", "Mumbai"),
    (19.1612, 72.8801, "unsafe_area",    "Isolated forest road. Mumbai Police flagged as unsafe for women at night.", "night", "Aarey Colony", "Mumbai"),
    (19.1578, 72.8812, "stalking",       "Woman followed by unknown man near Aarey Colony gate.", "night", "Aarey Colony", "Mumbai"),
    (19.1634, 72.8756, "poor_lighting",  "No functioning street lights on main Aarey road past 10pm.", "late_night", "Aarey Colony", "Mumbai"),

    # ── Old Mill Compounds – Lower Parel ─────────
    (19.0178, 72.8478, "unsafe_area",    "Abandoned mill compound. No security or lighting after work hours.", "night", "Lower Parel Mills", "Mumbai"),
    (19.0165, 72.8461, "poor_lighting",  "Mill compound lane completely dark at night. Avoid.", "late_night", "Lower Parel Mills", "Mumbai"),
    (19.0201, 72.8490, "harassment",     "Group of men loitering near mill gate at night.", "late_night", "Worli", "Mumbai"),
    (19.0189, 72.8502, "unsafe_area",    "Deserted compound road. No pedestrians after 9pm.", "night", "Lower Parel", "Mumbai"),
    (19.0212, 72.8455, "poor_lighting",  "Broken street lights near Kamala Mills back entrance.", "night", "Lower Parel", "Mumbai"),

    # ── South Mumbai Subways / Bylanes ───────────
    (18.9388, 72.8354, "poor_lighting",  "Subway under CST poorly lit. Mumbai Police listed as unsafe.", "night", "CST Subway", "Mumbai"),
    (18.9402, 72.8368, "harassment",     "Harassment reported on CST late night platforms.", "late_night", "CST Area", "Mumbai"),
    (18.9220, 72.8347, "unsafe_area",    "Dark bylane near Colaba causeway. Avoid after 11pm.", "late_night", "Colaba", "Mumbai"),
    (18.9198, 72.8312, "stalking",       "Stalking reported near Colaba market closed shops area.", "late_night", "Colaba", "Mumbai"),
    (18.9367, 72.8401, "poor_lighting",  "Subway near Marine Lines station completely dark.", "night", "Marine Lines", "Mumbai"),
    (18.9289, 72.8289, "harassment",     "Verbal harassment near Nariman Point parking area at night.", "night", "Nariman Point", "Mumbai"),

    # ── Chowpatty Beach ──────────────────────────
    (18.9548, 72.8122, "harassment",     "Verbal harassment and stalking at Chowpatty beach at night.", "night", "Chowpatty Beach", "Mumbai"),
    (18.9535, 72.8108, "unsafe_area",    "Beach area deserted and unsafe after 10pm.", "late_night", "Chowpatty Beach", "Mumbai"),
    (18.9562, 72.8134, "stalking",       "Man followed woman from beach towards Walkeshwar road.", "night", "Chowpatty Beach", "Mumbai"),

    # ── Dadar Skywalk ────────────────────────────
    (19.0760, 72.8401, "poor_lighting",  "Skywalk near Dadar station dimly lit and poorly maintained.", "night", "Dadar Skywalk", "Mumbai"),
    (19.0748, 72.8389, "harassment",     "Stalking incidents on Dadar skywalk at night.", "late_night", "Dadar", "Mumbai"),
    (19.0778, 72.8412, "unsafe_area",    "Skywalk deserted after midnight. Avoid alone.", "late_night", "Dadar", "Mumbai"),

    # ── Andheri ──────────────────────────────────
    (19.1136, 72.8697, "harassment",     "Harassment near Andheri station east side at night.", "evening", "Andheri East", "Mumbai"),
    (19.1197, 72.8464, "theft",          "Phone snatching near Andheri west market.", "evening", "Andheri West", "Mumbai"),
    (19.1089, 72.8674, "poor_lighting",  "Back lanes of Andheri east completely unlit.", "night", "Andheri East", "Mumbai"),
    (19.1156, 72.8712, "stalking",       "Woman followed from metro station towards residential area.", "night", "Andheri East", "Mumbai"),
    (19.1223, 72.8478, "unsafe_area",    "Deserted road behind Andheri west station after 11pm.", "late_night", "Andheri West", "Mumbai"),
    (19.1178, 72.8501, "harassment",     "Catcalling near Andheri west food stalls at night.", "evening", "Andheri West", "Mumbai"),

    # ── Kurla ────────────────────────────────────
    (19.0653, 72.8793, "unsafe_area",    "Kurla station surroundings unsafe especially east side.", "late_night", "Kurla", "Mumbai"),
    (19.0701, 72.8821, "harassment",     "Multiple harassment reports near Kurla bus depot.", "night", "Kurla", "Mumbai"),
    (19.0629, 72.8762, "theft",          "Bag snatching near Kurla market area.", "evening", "Kurla", "Mumbai"),
    (19.0678, 72.8834, "poor_lighting",  "No lights near Kurla east flyover underpass.", "night", "Kurla East", "Mumbai"),
    (19.0712, 72.8798, "stalking",       "Stalking near Kurla LBS road at night.", "late_night", "Kurla", "Mumbai"),

    # ── Dharavi ──────────────────────────────────
    (19.0400, 72.8536, "unsafe_area",    "Isolated lanes inside Dharavi after dark. Avoid.", "late_night", "Dharavi", "Mumbai"),
    (19.0445, 72.8512, "poor_lighting",  "No street lights in interior Dharavi lanes.", "night", "Dharavi", "Mumbai"),
    (19.0389, 72.8578, "harassment",     "Harassment reported near Dharavi main road at night.", "evening", "Dharavi", "Mumbai"),
    (19.0412, 72.8498, "unsafe_area",    "Deserted lanes near Dharavi 90 feet road after 10pm.", "night", "Dharavi", "Mumbai"),

    # ── Sion / Matunga ───────────────────────────
    (19.0445, 72.8623, "poor_lighting",  "Sion hospital road area poorly lit at night.", "night", "Sion", "Mumbai"),
    (19.0478, 72.8601, "harassment",     "Harassment near Sion station at night.", "evening", "Sion", "Mumbai"),
    (19.0523, 72.8645, "unsafe_area",    "Isolated road near Sion fort area after dark.", "late_night", "Sion", "Mumbai"),
    (19.0556, 72.8589, "theft",          "Phone snatched near Matunga station.", "evening", "Matunga", "Mumbai"),

    # ── Bandra ───────────────────────────────────
    (19.0544, 72.8407, "harassment",     "Verbal harassment near Bandra station west at night.", "evening", "Bandra West", "Mumbai"),
    (19.0489, 72.8378, "poor_lighting",  "Lane behind Bandra station poorly lit.", "night", "Bandra West", "Mumbai"),
    (19.0512, 72.8356, "stalking",       "Woman followed near Bandra reclamation area at night.", "night", "Bandra West", "Mumbai"),
    (19.0601, 72.8423, "unsafe_area",    "Bandra east slum road deserted after 10pm.", "late_night", "Bandra East", "Mumbai"),

    # ── Malad / Kandivali ────────────────────────
    (19.1868, 72.8484, "unsafe_area",    "Malad creek road deserted and unsafe at night.", "late_night", "Malad West", "Mumbai"),
    (19.1923, 72.8512, "poor_lighting",  "Malad east back road near creek completely dark.", "night", "Malad East", "Mumbai"),
    (19.1845, 72.8456, "harassment",     "Harassment near Malad station west at night.", "evening", "Malad West", "Mumbai"),
    (19.2134, 72.8523, "unsafe_area",    "Isolated road near Kandivali east MIDC at night.", "late_night", "Kandivali East", "Mumbai"),
    (19.2167, 72.8501, "poor_lighting",  "No street lights near Kandivali station east exit.", "night", "Kandivali East", "Mumbai"),

    # ── Borivali ─────────────────────────────────
    (19.2307, 72.8567, "poor_lighting",  "Borivali national park boundary road — no lights.", "night", "Borivali", "Mumbai"),
    (19.2289, 72.8534, "unsafe_area",    "Forest road near Borivali national park. Deserted at night.", "late_night", "Borivali", "Mumbai"),
    (19.2345, 72.8589, "harassment",     "Harassment reported near Borivali station east side.", "evening", "Borivali East", "Mumbai"),

    # ── Jogeshwari / Goregaon ────────────────────
    (19.0890, 72.8650, "unsafe_area",    "Construction zone near Jogeshwari. No security at night.", "night", "Jogeshwari", "Mumbai"),
    (19.0923, 72.8623, "poor_lighting",  "Broken lights near Jogeshwari west station exit.", "night", "Jogeshwari West", "Mumbai"),
    (19.1278, 72.8512, "harassment",     "Harassment near Goregaon station east side.", "evening", "Goregaon East", "Mumbai"),
    (19.1312, 72.8489, "theft",          "Phone snatching near Goregaon market area.", "evening", "Goregaon East", "Mumbai"),

    # ── Vikhroli / Bhandup ───────────────────────
    (19.1089, 72.9234, "poor_lighting",  "Vikhroli industrial area road completely dark after work hours.", "night", "Vikhroli East", "Mumbai"),
    (19.1123, 72.9267, "unsafe_area",    "Isolated stretch near Vikhroli pipe road. No people at night.", "late_night", "Vikhroli", "Mumbai"),
    (19.1389, 72.9312, "poor_lighting",  "Bhandup station road poorly lit. No lights near bridge.", "night", "Bhandup", "Mumbai"),
    (19.1412, 72.9289, "harassment",     "Harassment near Bhandup station at night.", "evening", "Bhandup", "Mumbai"),

    # ── Mulund / Thane border ────────────────────
    (19.1723, 72.9534, "unsafe_area",    "Mulund check naka area deserted and unsafe at night.", "late_night", "Mulund West", "Mumbai"),
    (19.1756, 72.9512, "poor_lighting",  "No street lights near Mulund toll naka stretch.", "night", "Mulund East", "Mumbai"),
    (19.1689, 72.9489, "stalking",       "Stalking reported near Mulund station at night.", "night", "Mulund", "Mumbai"),

    # ── Govandi / Mankhurd / Trombay ─────────────
    (19.0512, 72.9234, "unsafe_area",    "Govandi station area extremely unsafe at night.", "late_night", "Govandi", "Mumbai"),
    (19.0489, 72.9212, "harassment",     "Multiple harassment cases near Govandi slum roads.", "night", "Govandi", "Mumbai"),
    (19.0423, 72.9178, "poor_lighting",  "Mankhurd road near dumping ground — no lights, isolated.", "night", "Mankhurd", "Mumbai"),
    (19.0456, 72.9156, "unsafe_area",    "Mankhurd bridge road completely deserted after 9pm.", "late_night", "Mankhurd", "Mumbai"),
    (19.0178, 72.9289, "poor_lighting",  "Trombay road near BARC boundary — dark and isolated.", "night", "Trombay", "Mumbai"),

    # ── Mira Road / Vasai border ─────────────────
    (19.2856, 72.8712, "unsafe_area",    "Mira Road station area back lanes unsafe at night.", "late_night", "Mira Road", "Mumbai"),
    (19.2889, 72.8734, "harassment",     "Harassment near Mira Road east market at night.", "evening", "Mira Road East", "Mumbai"),
    (19.3234, 72.8823, "poor_lighting",  "Vasai road stretch no lights near railway crossing.", "night", "Vasai Road", "Mumbai"),

    # ── Navi Mumbai ──────────────────────────────
    (19.0330, 73.0297, "unsafe_area",    "Vashi sector 9 back road isolated at night.", "late_night", "Vashi", "Mumbai"),
    (19.0312, 73.0312, "poor_lighting",  "Vashi station road — lights broken near flyover.", "night", "Vashi", "Mumbai"),
    (19.0445, 73.0134, "harassment",     "Harassment near Turbhe MIDC at night.", "night", "Turbhe", "Mumbai"),
    (19.0678, 73.0089, "unsafe_area",    "Ghansoli road near creek completely isolated.", "late_night", "Ghansoli", "Mumbai"),

    # ════════════════════════════════════════════
    # DELHI
    # ════════════════════════════════════════════

    # ── Paharganj ────────────────────────────────
    (28.6448, 77.2130, "harassment",     "Paharganj main bazaar — heavy harassment after 9pm.", "night", "Paharganj", "Delhi"),
    (28.6461, 77.2098, "unsafe_area",    "Narrow lanes behind Paharganj. Multiple incidents reported.", "late_night", "Paharganj", "Delhi"),
    (28.6472, 77.2156, "stalking",       "Stalking and following women near Paharganj.", "evening", "Paharganj", "Delhi"),
    (28.6438, 77.2112, "poor_lighting",  "Back alleys of Paharganj completely dark at night.", "late_night", "Paharganj", "Delhi"),
    (28.6455, 77.2167, "theft",          "Phone and wallet snatching near Paharganj market.", "evening", "Paharganj", "Delhi"),

    # ── Kashmere Gate / Old Delhi ────────────────
    (28.6692, 77.2291, "harassment",     "Harassment near Kashmere Gate ISBT. Unsafe at night.", "night", "Kashmere Gate", "Delhi"),
    (28.6701, 77.2278, "theft",          "Bag snatching near Kashmere Gate bus terminal.", "evening", "Kashmere Gate", "Delhi"),
    (28.6723, 77.2312, "unsafe_area",    "Old Delhi lanes near Kashmere Gate. Avoid after dark.", "late_night", "Old Delhi", "Delhi"),
    (28.6678, 77.2256, "poor_lighting",  "Poorly lit roads near Kashmere Gate metro.", "night", "Kashmere Gate", "Delhi"),
    (28.6534, 77.2345, "harassment",     "Harassment near Chandni Chowk market at night.", "evening", "Chandni Chowk", "Delhi"),
    (28.6512, 77.2312, "theft",          "Snatching near Chandni Chowk metro station.", "evening", "Chandni Chowk", "Delhi"),
    (28.6589, 77.2289, "unsafe_area",    "Isolated lanes near Jama Masjid after closing time.", "late_night", "Jama Masjid", "Delhi"),

    # ── Connaught Place ──────────────────────────
    (28.6315, 77.2167, "harassment",     "Harassment and catcalling near CP inner circle at night.", "night", "Connaught Place", "Delhi"),
    (28.6289, 77.2198, "theft",          "Phone snatching near Rajiv Chowk metro exit.", "evening", "Connaught Place", "Delhi"),
    (28.6334, 77.2145, "stalking",       "Stalking near CP outer circle parking area.", "late_night", "Connaught Place", "Delhi"),
    (28.6301, 77.2223, "poor_lighting",  "Underground parking area near CP poorly lit.", "night", "Connaught Place", "Delhi"),

    # ── Dwarka ───────────────────────────────────
    (28.5562, 77.1000, "poor_lighting",  "Sector 12 Dwarka — street lights non-functional for months.", "night", "Dwarka Sector 12", "Delhi"),
    (28.5489, 77.0934, "unsafe_area",    "Isolated stretch near Dwarka Sector 9 metro at night.", "late_night", "Dwarka", "Delhi"),
    (28.5612, 77.1078, "harassment",     "Harassment near Dwarka Sector 10 park area at night.", "night", "Dwarka", "Delhi"),
    (28.5678, 77.0912, "stalking",       "Stalking near Dwarka Sector 6 metro station.", "evening", "Dwarka Sector 6", "Delhi"),
    (28.5534, 77.1123, "poor_lighting",  "Dwarka Sector 14 back roads completely dark.", "night", "Dwarka Sector 14", "Delhi"),
    (28.5745, 77.0867, "unsafe_area",    "Dwarka Sector 3 isolated road near drain. Avoid at night.", "late_night", "Dwarka Sector 3", "Delhi"),

    # ── Rohini ───────────────────────────────────
    (28.7041, 77.1025, "harassment",     "Rohini Sector 3 market — harassment near closed shops at night.", "late_night", "Rohini", "Delhi"),
    (28.7108, 77.0978, "poor_lighting",  "Rohini west isolated roads. No lights at night.", "night", "Rohini West", "Delhi"),
    (28.6989, 77.1123, "unsafe_area",    "Construction area near Rohini East metro. Isolated.", "late_night", "Rohini East", "Delhi"),
    (28.7156, 77.1067, "stalking",       "Stalking near Rohini Sector 7 market at night.", "night", "Rohini Sector 7", "Delhi"),
    (28.7023, 77.0956, "theft",          "Snatching near Rithala metro station.", "evening", "Rithala", "Delhi"),

    # ── Laxmi Nagar / East Delhi ─────────────────
    (28.6297, 77.2769, "harassment",     "Laxmi Nagar market area — frequent harassment reports.", "evening", "Laxmi Nagar", "Delhi"),
    (28.6312, 77.2812, "theft",          "Snatching near Laxmi Nagar metro station.", "evening", "Laxmi Nagar", "Delhi"),
    (28.6278, 77.2834, "poor_lighting",  "Back roads of Laxmi Nagar poorly lit at night.", "night", "Laxmi Nagar", "Delhi"),
    (28.6334, 77.2756, "unsafe_area",    "Isolated lane near Laxmi Nagar drain area at night.", "late_night", "Laxmi Nagar", "Delhi"),

    # ── Saket / South Delhi ──────────────────────
    (28.5244, 77.2066, "poor_lighting",  "Saket back lanes near PVR poorly lit at night.", "night", "Saket", "Delhi"),
    (28.5198, 77.2089, "unsafe_area",    "Isolated road near Saket court complex after hours.", "late_night", "Saket", "Delhi"),
    (28.5267, 77.2034, "stalking",       "Stalking near Saket metro station at night.", "night", "Saket", "Delhi"),

    # ── Noida Border / Badarpur ──────────────────
    (28.5355, 77.3910, "unsafe_area",    "Noida-Delhi border stretch. Poorly monitored at night.", "late_night", "Noida Border", "Delhi"),
    (28.5401, 77.3956, "harassment",     "Harassment near Noida border industrial area.", "night", "Noida Border", "Delhi"),
    (28.5023, 77.2934, "unsafe_area",    "Badarpur border road. Trucks parked at night, no lighting.", "late_night", "Badarpur", "Delhi"),
    (28.5045, 77.2912, "poor_lighting",  "Badarpur main road lights broken near flyover.", "night", "Badarpur", "Delhi"),
    (28.5067, 77.2956, "harassment",     "Harassment near Badarpur metro station at night.", "evening", "Badarpur", "Delhi"),

    # ── Civil Lines / North Delhi ────────────────
    (28.6861, 77.2311, "poor_lighting",  "Civil Lines roads near university gates dark at night.", "late_night", "Civil Lines", "Delhi"),
    (28.6834, 77.2289, "stalking",       "Stalking near Delhi University north campus.", "night", "Civil Lines", "Delhi"),
    (28.6878, 77.2334, "harassment",     "Harassment near GTB Nagar metro station at night.", "evening", "GTB Nagar", "Delhi"),
    (28.6912, 77.2267, "unsafe_area",    "Isolated road near Vidhan Sabha metro at night.", "late_night", "Civil Lines", "Delhi"),

    # ── Uttam Nagar ──────────────────────────────
    (28.6211, 77.0589, "unsafe_area",    "Uttam Nagar west lanes — frequent incidents reported.", "night", "Uttam Nagar", "Delhi"),
    (28.6189, 77.0623, "harassment",     "Harassment near Uttam Nagar market at night.", "late_night", "Uttam Nagar", "Delhi"),
    (28.6234, 77.0556, "poor_lighting",  "Uttam Nagar east road near drain completely dark.", "night", "Uttam Nagar East", "Delhi"),
    (28.6178, 77.0601, "theft",          "Snatching near Uttam Nagar metro station.", "evening", "Uttam Nagar", "Delhi"),

    # ── Sangam Vihar / Deoli ─────────────────────
    (28.4989, 77.2534, "unsafe_area",    "Sangam Vihar outer lanes. No police patrolling at night.", "late_night", "Sangam Vihar", "Delhi"),
    (28.5012, 77.2512, "poor_lighting",  "Sangam Vihar main road — broken lights for months.", "night", "Sangam Vihar", "Delhi"),
    (28.5034, 77.2489, "harassment",     "Harassment near Sangam Vihar market at night.", "evening", "Sangam Vihar", "Delhi"),
    (28.4967, 77.2567, "stalking",       "Stalking reported near Deoli area at night.", "night", "Deoli", "Delhi"),

    # ── Mustafabad / Seelampur ───────────────────
    (28.7234, 77.2823, "unsafe_area",    "Mustafabad lanes extremely unsafe at night.", "late_night", "Mustafabad", "Delhi"),
    (28.7256, 77.2845, "harassment",     "Multiple harassment incidents near Mustafabad market.", "evening", "Mustafabad", "Delhi"),
    (28.7189, 77.2789, "poor_lighting",  "No working street lights in Mustafabad residential area.", "night", "Mustafabad", "Delhi"),
    (28.6934, 77.2823, "unsafe_area",    "Seelampur station area unsafe especially for women at night.", "late_night", "Seelampur", "Delhi"),
    (28.6956, 77.2845, "harassment",     "Harassment near Seelampur metro station at night.", "night", "Seelampur", "Delhi"),

    # ── Trilokpuri / Kondli ──────────────────────
    (28.6178, 77.3123, "unsafe_area",    "Trilokpuri block 20 lanes isolated at night.", "late_night", "Trilokpuri", "Delhi"),
    (28.6201, 77.3145, "poor_lighting",  "No lights near Trilokpuri east drain road.", "night", "Trilokpuri", "Delhi"),
    (28.6223, 77.3167, "harassment",     "Harassment near Trilokpuri market area.", "evening", "Trilokpuri", "Delhi"),
    (28.6267, 77.3234, "unsafe_area",    "Kondli road near Yamuna isolated after dark.", "late_night", "Kondli", "Delhi"),

    # ── Okhla / Jamia ────────────────────────────
    (28.5489, 77.2734, "unsafe_area",    "Okhla industrial area roads deserted after work hours.", "night", "Okhla", "Delhi"),
    (28.5512, 77.2756, "poor_lighting",  "Okhla Phase 2 road no functioning street lights.", "night", "Okhla Phase 2", "Delhi"),
    (28.5601, 77.2823, "harassment",     "Harassment near Jamia Nagar at night.", "evening", "Jamia Nagar", "Delhi"),
    (28.5623, 77.2845, "stalking",       "Stalking near Jamia Millia university gate at night.", "night", "Jamia Nagar", "Delhi"),

    # ── Outer Ring Road stretches ────────────────
    (28.6489, 77.1234, "unsafe_area",    "Outer Ring Road near Punjabi Bagh — isolated at night.", "late_night", "Punjabi Bagh", "Delhi"),
    (28.6512, 77.1256, "poor_lighting",  "Outer ring road stretch near Madipur dark at night.", "night", "Madipur", "Delhi"),
    (28.5934, 77.1823, "unsafe_area",    "Ring road near Dhaula Kuan deserted late night.", "late_night", "Dhaula Kuan", "Delhi"),
    (28.5956, 77.1845, "harassment",     "Harassment near Dhaula Kuan bus stop at night.", "night", "Dhaula Kuan", "Delhi"),

    # ── Najafgarh ────────────────────────────────
    (28.6089, 76.9823, "unsafe_area",    "Najafgarh road extremely isolated at night. No patrols.", "late_night", "Najafgarh", "Delhi"),
    (28.6112, 76.9845, "poor_lighting",  "Najafgarh market road poorly lit. Avoid at night.", "night", "Najafgarh", "Delhi"),
    (28.6067, 76.9801, "harassment",     "Harassment near Najafgarh bus terminal at night.", "evening", "Najafgarh", "Delhi"),

    # ── Bus Terminals / Transport hubs ───────────
    (28.6356, 77.2234, "harassment",     "Anand Vihar ISBT — harassment at bus terminal at night.", "night", "Anand Vihar", "Delhi"),
    (28.6378, 77.2256, "theft",          "Snatching near Anand Vihar bus terminal.", "evening", "Anand Vihar", "Delhi"),
    (28.6401, 77.2278, "unsafe_area",    "Anand Vihar station area deserted after last metro.", "late_night", "Anand Vihar", "Delhi"),
    (28.6134, 77.2045, "harassment",     "Harassment at Sarai Kale Khan ISBT at night.", "night", "Sarai Kale Khan", "Delhi"),
    (28.6156, 77.2067, "theft",          "Bag snatching near Sarai Kale Khan bus terminal.", "evening", "Sarai Kale Khan", "Delhi"),

    # ── Nizamuddin / Hazrat Nizamuddin ───────────
    (28.5889, 77.2512, "unsafe_area",    "Nizamuddin railway station area unsafe at night.", "late_night", "Nizamuddin", "Delhi"),
    (28.5912, 77.2489, "harassment",     "Harassment near Nizamuddin dargah area at night.", "night", "Nizamuddin", "Delhi"),
    (28.5867, 77.2534, "poor_lighting",  "Road near Nizamuddin bridge poorly lit.", "night", "Nizamuddin", "Delhi"),

    # ── Shahdara / Dilshad Garden ────────────────
    (28.6712, 77.2956, "harassment",     "Harassment near Shahdara station at night.", "evening", "Shahdara", "Delhi"),
    (28.6734, 77.2978, "unsafe_area",    "Shahdara market back lanes isolated after closing.", "late_night", "Shahdara", "Delhi"),
    (28.6823, 77.3189, "poor_lighting",  "Dilshad Garden Sector C road no lights at night.", "night", "Dilshad Garden", "Delhi"),
    (28.6845, 77.3212, "stalking",       "Stalking near Dilshad Garden metro station.", "night", "Dilshad Garden", "Delhi"),

    # ── Wazirabad / Burari ───────────────────────
    (28.7423, 77.2234, "unsafe_area",    "Wazirabad road near Yamuna completely isolated at night.", "late_night", "Wazirabad", "Delhi"),
    (28.7445, 77.2256, "poor_lighting",  "No lights on Wazirabad bridge road after 10pm.", "night", "Wazirabad", "Delhi"),
    (28.7234, 77.2123, "harassment",     "Harassment near Burari market area at night.", "evening", "Burari", "Delhi"),
    (28.7256, 77.2145, "unsafe_area",    "Burari outer road deserted. No patrolling at night.", "late_night", "Burari", "Delhi"),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lat         REAL NOT NULL,
            lng         REAL NOT NULL,
            type        TEXT NOT NULL,
            description TEXT,
            time_of_day TEXT NOT NULL,
            area_name   TEXT NOT NULL,
            city        TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            upvotes     INTEGER DEFAULT 0
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    if count > 0:
        print(f"Database already has {count} incidents. Skipping seed.")
        conn.close()
        return

    now = datetime.utcnow()
    for row in INCIDENTS:
        days_ago  = random.randint(0, 45)
        hours_ago = random.randint(0, 23)
        created   = (now - timedelta(days=days_ago, hours=hours_ago)).isoformat()
        conn.execute(
            """INSERT INTO incidents
               (lat, lng, type, description, time_of_day, area_name, city, created_at, upvotes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (*row, created, random.randint(1, 15))
        )

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    mumbai = conn.execute("SELECT COUNT(*) FROM incidents WHERE city='Mumbai'").fetchone()[0]
    delhi  = conn.execute("SELECT COUNT(*) FROM incidents WHERE city='Delhi'").fetchone()[0]
    print(f"✅ Seeded {total} incidents — Mumbai: {mumbai}, Delhi: {delhi}")
    conn.close()


if __name__ == "__main__":
    seed()
