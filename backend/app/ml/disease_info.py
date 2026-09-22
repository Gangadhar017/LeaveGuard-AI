"""Agronomic knowledge base for detected diseases.

Keys are the human-readable class labels produced by app.ml.labels
(must stay in sync with the dataset folder names). Unknown classes fall back
to DEFAULT_INFO so a future model swap cannot break the API contract.
"""

from __future__ import annotations

HEALTHY_INFO = {
    "description": (
        "No disease symptoms were detected in the analyzed leaf. The coloration "
        "and texture patterns look consistent with healthy foliage."
    ),
    "symptoms": [],
    "prevention": [
        "Water at the base of plants in the morning to keep foliage dry.",
        "Mulch around the base to prevent soil-borne spores splashing onto leaves.",
        "Inspect leaves (especially the undersides) weekly for early symptoms.",
        "Ensure good airflow through proper spacing and pruning.",
    ],
    "treatment": [],
    "severity": "healthy",
}

KNOWLEDGE_BASE: dict[str, dict] = {
    "Tomato Bacterial Spot": {
        "description": (
            "Bacterial disease caused by Xanthomonas spp. It produces small "
            "water-soaked spots that turn dark and greasy, leading to "
            "defoliation and spotted, unmarketable fruit. It spreads quickly "
            "in warm, wet weather, especially via splashing rain."
        ),
        "symptoms": [
            "Small, water-soaked spots on the upper leaf surface.",
            "Spots turn dark brown or purplish with a yellow halo.",
            "Leaves yellow and drop prematurely.",
            "Raised, scabby spots on green fruit.",
        ],
        "prevention": [
            "Use certified disease-free seeds and transplants.",
            "Rotate out of tomato/pepper for at least 2 years.",
            "Avoid overhead irrigation; water at soil level.",
            "Space plants for airflow and avoid handling wet foliage.",
        ],
        "treatment": [
            "Apply copper-based bactericides at the first symptoms.",
            "Remove and destroy heavily infected plants — do not compost.",
            "Sanitize tools and wash hands after touching infected plants.",
        ],
        "severity": "high",
    },
    "Tomato Early Blight": {
        "description": (
            "Fungal disease caused by Alternaria solani. It forms distinctive "
            "concentric-ring 'target' lesions, usually on older leaves first, "
            "and thrives in warm, humid conditions. Severe infections defoliate "
            "plants and expose fruit to sunscald."
        ),
        "symptoms": [
            "Brown spots with concentric rings (target pattern).",
            "Lesions typically start on older, lower leaves.",
            "Yellowing of tissue surrounding the spots.",
            "Dark sunken cankers on stems at the soil line.",
        ],
        "prevention": [
            "Mulch to stop soil spores splashing onto leaves.",
            "Water at the base, early in the day.",
            "Rotate with non-solanaceous crops and stake plants.",
            "Maintain balanced fertility; stressed plants are more susceptible.",
        ],
        "treatment": [
            "Apply labeled fungicides (chlorothalonil, copper) at first signs.",
            "Prune off and destroy infected lower leaves.",
            "Remove crop debris at the end of the season.",
        ],
        "severity": "medium",
    },
    "Tomato Late Blight": {
        "description": (
            "Extremely destructive disease caused by the oomycete Phytophthora "
            "infestans (the pathogen behind the Irish potato famine). Under "
            "cool, wet conditions it can kill a tomato planting within days "
            "and spreads via airborne spores."
        ),
        "symptoms": [
            "Greasy, gray-green water-soaked patches on leaves.",
            "White fuzzy mold on leaf undersides in humid weather.",
            "Rapid browning and blackening of entire foliage.",
            "Brown greasy stem streaks and firm brown fruit lesions.",
        ],
        "prevention": [
            "Plant certified disease-free seed potatoes and tomato transplants.",
            "Destroy volunteer tomato/potato plants and cull piles.",
            "Space plants widely and avoid overhead watering.",
            "Monitor closely during cool, wet periods.",
        ],
        "treatment": [
            "Apply protective fungicides (chlorothalonil, mancozeb) before "
            "infection windows.",
            "Remove and bag infected plants immediately — never compost.",
            "Report outbreaks to local extension services where available.",
        ],
        "severity": "critical",
    },
    "Tomato Leaf Mold": {
        "description": (
            "Fungal disease caused by Passalora fulva, favored by humidity "
            "above 85% — a classic greenhouse problem. Pale spots appear on "
            "the upper leaf surface with characteristic olive-green mold below."
        ),
        "symptoms": [
            "Pale green to yellow spots on the upper leaf surface.",
            "Olive-green to gray fuzzy mold on the leaf underside.",
            "Leaves curl, wither and drop, starting from lower leaves.",
            "Infections can also strike blossoms and fruit.",
        ],
        "prevention": [
            "Ventilate greenhouses; keep relative humidity below 85%.",
            "Space and prune plants for airflow.",
            "Disinfect structures between growing seasons.",
            "Grow resistant cultivars where available.",
        ],
        "treatment": [
            "Apply fungicides labeled for leaf mold.",
            "Remove and destroy infected lower foliage.",
            "Reduce leaf wetness duration and improve air circulation.",
        ],
        "severity": "medium",
    },
    "Tomato Septoria Leaf Spot": {
        "description": (
            "Fungal disease caused by Septoria lycopersici, usually appearing "
            "right after fruit set. It produces numerous small spots on lower "
            "leaves and can rapidly defoliate plants, reducing yield and "
            "exposing fruit to sunscald."
        ),
        "symptoms": [
            "Small round spots (~3 mm) with dark brown margins.",
            "Gray or tan centers dotted with tiny black fruiting bodies.",
            "Symptoms begin on lower leaves after fruit set.",
            "Leaves yellow and fall off as spots merge.",
        ],
        "prevention": [
            "Remove and dispose of all tomato debris at season end.",
            "Mulch and water at soil level to avoid wet foliage.",
            "Rotate crops for at least 2 years.",
            "Stake and prune to keep foliage off the ground.",
        ],
        "treatment": [
            "Apply copper or chlorothalonil fungicides at first appearance.",
            "Remove severely infected leaves and destroy them.",
            "Avoid working among plants while foliage is wet.",
        ],
        "severity": "medium",
    },
    "Tomato Healthy": HEALTHY_INFO,
    "Potato Early Blight": {
        "description": (
            "Fungal disease caused by Alternaria solani affecting potato "
            "foliage. It produces brown 'target-board' lesions on older leaves "
            "and can reduce tuber yield when defoliation is severe."
        ),
        "symptoms": [
            "Dark brown spots with concentric rings on older leaves.",
            "A narrow yellow chlorotic zone around each lesion.",
            "Irregular brown stem lesions later in the season.",
            "Premature leaf drop starting from the bottom of the plant.",
        ],
        "prevention": [
            "Use healthy certified seed and resistant varieties.",
            "Rotate with cereals or other non-host crops.",
            "Maintain plant vigor with balanced nutrition and irrigation.",
            "Incorporate crop residues after harvest.",
        ],
        "treatment": [
            "Apply protectant fungicides when lesions first appear.",
            "Irrigate to avoid prolonged leaf wetness.",
            "Hill potatoes well and harvest promptly once tubers mature.",
        ],
        "severity": "medium",
    },
    "Potato Late Blight": {
        "description": (
            "The most serious potato disease worldwide, caused by Phytophthora "
            "infestans. Foliar infections turn plants black within days and "
            "the pathogen can also rot tubers in storage."
        ),
        "symptoms": [
            "Water-soaked pale green lesions with darker edges on leaves.",
            "White mold rings on leaf undersides under humid conditions.",
            "Blackened stems and rapid canopy collapse.",
            "Reddish-brown, granular dry rot inside infected tubers.",
        ],
        "prevention": [
            "Plant certified disease-free seed potatoes only.",
            "Eliminate volunteer potatoes and cull piles.",
            "Keep good airflow and avoid sprinkler irrigation in cool spells.",
            "Hill soil high to protect tubers from spore wash-down.",
        ],
        "treatment": [
            "Begin protectant fungicide programs before blight weather.",
            "Destroy infection hotspots immediately (bag and remove plants).",
            "Delay harvest until infected foliage is fully dead, then cure "
            "tubers properly before storage.",
        ],
        "severity": "critical",
    },
    "Potato Healthy": HEALTHY_INFO,
}

DEFAULT_INFO = {
    "description": (
        "The model classified this leaf, but no curated agronomic information "
        "exists for this class yet. Please verify the result visually and "
        "consult a local agricultural extension service for guidance."
    ),
    "symptoms": [],
    "prevention": [
        "Keep foliage dry when watering and ensure good airflow.",
        "Remove obviously diseased leaves and dispose of them away from the garden.",
    ],
    "treatment": [],
    "severity": "unknown",
}


def get_disease_info(label: str) -> dict:
    return KNOWLEDGE_BASE.get(label, DEFAULT_INFO)
