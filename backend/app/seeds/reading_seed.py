"""Idempotent seed data for Milestone 1:
1. Original 3-passage, 40-question IELTS Academic Reading Mock Test (100% newly authored,
   calibrated to IDP taxonomy & Cambridge structural benchmarks; zero copyrighted material).
2. Curated starter strategy notes loaded from data/notes/reading_starter_notes.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.db.models import KnowledgeConcept, QuestionItem, ReadingTest
from pipelines.schemas import StrategyNote

READING_TEST_ID = "acad-reading-mock-01"

PASSAGES: list[dict[str, Any]] = [
    {
        "index": 1,
        "title": "The Architecture of Early Tidal Mills",
        "subtitle": "How coastal engineers harnessed lunar rhythms centuries before modern turbines",
        "topic": "History of Engineering",
        "recommended_minutes": 20,
        "paragraphs": [
            {
                "id": "A",
                "text": (
                    "Long before coal-fired engines reshaped European manufacturing, coastal communities along the "
                    "Atlantic seaboard had already mastered a remarkably dependable renewable power source: the daily "
                    "rise and fall of the ocean tide. Archaeological excavations at Nendrum Monastery in Northern Ireland "
                    "uncovered timber sluices and a stone millpond dating back to 787 CE, pushing the documented origins "
                    "of tidal milling in northwestern Europe nearly three centuries earlier than historians once assumed. "
                    "Unlike inland watermills, which frequently stalled during summer droughts or froze solid in harsh "
                    "winters, tidal installations drew upon saline estuaries that remained ice-free and followed an "
                    "unbroken astronomical timetable."
                ),
            },
            {
                "id": "B",
                "text": (
                    "The underlying principle of a traditional tide mill was deceptively simple yet demanded meticulous "
                    "civil engineering. Builders constructed an earthen or masonry dam across a narrow tidal creek to "
                    "create an impounded reservoir known as a millpond. As the incoming flood tide rose, hinged wooden "
                    "flap gates swung inward automatically, allowing seawater to fill the basin. Once the tide reached "
                    "its peak and began to ebb, the reversing water pressure forced those same gates tightly shut, "
                    "trapping millions of litres behind the dam. Millers then waited roughly two to three hours until "
                    "the sea level outside dropped sufficiently to establish an effective head of water."
                ),
            },
            {
                "id": "C",
                "text": (
                    "When the miller lifted a vertical sluice gate, the trapped water rushed through a narrow timber "
                    "chute onto an undershot waterwheel, turning heavy millstones to grind wheat, barley, or oats into "
                    "flour. Because lunar cycles shift approximately fifty minutes later each day, a tidal miller's "
                    "working schedule migrated steadily around the clock. In coastal Suffolk and Brittany, families "
                    "routinely began grinding grain at three in the morning during one week and late in the afternoon "
                    "a fortnight later. Far from being viewed as an inconvenience, this predictable drift allowed "
                    "coastal merchants to coordinate barge deliveries with high water, when cargo vessels could float "
                    "directly beside the granary wharf."
                ),
            },
            {
                "id": "D",
                "text": (
                    "Sustaining a tide mill over several decades required relentless vigilance against two natural "
                    "adversaries: siltation and marine borers. Estuarine tides carried suspended mud that settled "
                    "quietly across the floor of the millpond, gradually shrinking its storage capacity. If left "
                    "unmanaged, a basin could lose half its volume within a single generation. Operators therefore "
                    "performed periodic scouring runs, opening bottom culverts at dead low tide so the rushing outflow "
                    "swept accumulated sediment back out to sea. Submerged oak pilings, meanwhile, were vulnerable to "
                    "shipworms—molluscs capable of honeycombing untreated wood—prompting builders in Devon and Maine "
                    "to sheath critical frames in copper sheeting or scorch the timber surface with fire."
                ),
            },
            {
                "id": "E",
                "text": (
                    "By the late eighteenth century, more than seven hundred tidal mills operated across Britain, "
                    "France, Spain, and colonial North America. Although grain milling remained their primary function, "
                    "ingenious entrepreneurs adapted tidal power to saw timber, crush mineral ore, full woollen cloth, "
                    "and even pump municipal drinking water beneath London Bridge. At Woodbridge Tide Mill in Suffolk, "
                    "restored machinery demonstrates how iron bevel gears introduced during the Industrial Revolution "
                    "boosted rotational efficiency without abandoning the centuries-old impounding basin."
                ),
            },
            {
                "id": "F",
                "text": (
                    "The eventual decline of tidal mills in the nineteenth century stemmed not from a failure of the "
                    "ocean resource itself, but from shifting economic expectations. Steam-powered roller mills could "
                    "be sited next to urban railway terminals rather than remote estuaries and ran continuously on "
                    "fixed twelve-hour factory shifts. Rail freight eroded the transport advantage once enjoyed by "
                    "coastal barges, while municipal drainage schemes reclaimed many shallow salt marshes for "
                    "agriculture. By 1930, fewer than a dozen commercial tide mills were still turning stone wheels."
                ),
            },
            {
                "id": "G",
                "text": (
                    "In recent decades, marine engineers investigating tidal range lagoons have revisited historic "
                    "mill records with renewed appreciation. Detailed Victorian logbooks from the Rance estuary and "
                    "the Severn basin preserve multi-decade observations of local spring-neap cycles and estuarine "
                    "sediment transport. While modern tidal barrages employ reversible bulb turbines rather than oak "
                    "paddles, they confront the exact same ecological trade-off documented by medieval millers: "
                    "capturing predictable marine energy while preserving intertidal mudflats that sustain migratory "
                    "shorebirds and juvenile fish."
                ),
            },
        ],
        "question_groups": [
            {
                "id": "p1-g1",
                "title": "Questions 1–6",
                "question_type": "tfng",
                "instructions": (
                    "Do the following statements agree with the information given in Reading Passage 1? "
                    "Choose TRUE if the statement agrees with the information, FALSE if it contradicts the "
                    "information, or NOT GIVEN if there is no information on this."
                ),
                "question_numbers": [1, 2, 3, 4, 5, 6],
            },
            {
                "id": "p1-g2",
                "title": "Questions 7–13",
                "question_type": "note_table_flowchart_completion",
                "instructions": (
                    "Complete the notes below. Choose ONE WORD ONLY from the passage for each answer."
                ),
                "word_limit": {
                    "max_words": 1,
                    "allow_number": False,
                    "label": "ONE WORD ONLY",
                },
                "note_heading": "Operation, Maintenance, and Legacy of Early Tidal Mills",
                "question_numbers": [7, 8, 9, 10, 11, 12, 13],
            },
        ],
    },
    {
        "index": 2,
        "title": "Rewilding Post-Industrial Corridors",
        "subtitle": "Turning abandoned railway embankments and factory canals into resilient urban ecosystems",
        "topic": "Urban Ecology & Environmental Science",
        "recommended_minutes": 20,
        "paragraphs": [
            {
                "id": "A",
                "text": (
                    "Across Europe and North America, thousands of kilometres of disused freight lines, slag heaps, "
                    "and canal towpaths wind through dense metropolitan districts. For decades, municipal planners "
                    "categorized these linear brownfields as eyesores awaiting expensive remediation and commercial "
                    "redevelopment. Yet botanical surveys conducted since the early 2000s have overturned that "
                    "assumption: undisturbed railway ballast and limestone quarry edges often harbour a higher "
                    "diversity of native wildflowers and solitary bees than manicured civic parks half a kilometre "
                    "away. Because heavy industrial soils are typically low in nitrogen, fast-growing aggressive weeds "
                    "struggle to dominate, leaving ecological space for rare stress-tolerant flora."
                ),
            },
            {
                "id": "B",
                "text": (
                    "Ecological connectivity explains why narrow industrial strips punch far above their surface area "
                    "in conservation value. Urban biologist Dr. Clara Lindholm has demonstrated through GPS tracking "
                    "of hedgehogs and nocturnal moths in Stockholm that isolated pocket parks act as demographic "
                    "traps when surrounded by multi-lane arterial roads. By contrast, continuous vegetated railway "
                    "verges function as biological highways, enabling genetic exchange between peripheral woodlands "
                    "and inner-city gardens. Even a corridor only eight metres wide significantly lowers local "
                    "extinction rates for ground-dwelling beetles, provided overhanging scrub remains unfragmented."
                ),
            },
            {
                "id": "C",
                "text": (
                    "Transforming contaminated infrastructure into safe public corridors nevertheless presents "
                    "formidable chemical and financial hurdles. Former railyards frequently contain heavy metals "
                    "such as lead, arsenic, and polycyclic aromatic hydrocarbons left behind by creosote sleepers "
                    "and locomotive exhaust. Environmental engineer Mateo Alvarez warns that excavating and trucking "
                    "polluted earth to hazardous landfills can consume up to seventy percent of a city's green-space "
                    "budget while generating substantial carbon emissions. Instead, Alvarez champions phytoremediation: "
                    "planting willow thickets and Indian mustard cultivars that immobilize or gradually draw down "
                    "soil toxins in situ before public footpaths are opened."
                ),
            },
            {
                "id": "D",
                "text": (
                    "Equally delicate is the social reception of wilder urban landscapes. Sociologist Dr. Hannah "
                    "Okafor interviewed residents living beside newly rewilded canal corridors in Sheffield and "
                    "Antwerp and observed a sharp divide in perception. While ecologists celebrated deadwood logs "
                    "and unmown seed heads as prime pollinator habitat, many long-term neighbours initially "
                    "interpreted tall dry grass as municipal neglect or an invitation to illegal dumping. Okafor "
                    "found that adding minimal 'cues to care'—such as crisp mown border strips along pathways, "
                    "interpretive signage explaining seasonal meadow cycles, and timber benches—raised neighbourhood "
                    "approval ratings dramatically without compromising biodiversity."
                ),
            },
            {
                "id": "E",
                "text": (
                    "Success in urban rewilding has also sparked an unintended real-estate phenomenon termed "
                    "'ecological gentrification'. Economist Prof. Kenji Takahashi tracked housing transactions "
                    "adjacent to flagship elevated rail-park conversions in New York, Paris, and Seoul. Within five "
                    "years of opening, median residential rents within three blocks rose between eighteen and "
                    "thirty-four percent faster than citywide averages, displacing lower-income tenants who had "
                    "endured decades of industrial noise and air pollution. Takahashi argues that green corridor "
                    "projects must be paired from inception with community land trusts or rent-stabilized housing "
                    "quotas, otherwise ecological restoration risks becoming a luxury amenity."
                ),
            },
            {
                "id": "F",
                "text": (
                    "Looking ahead, hydrologists see post-industrial corridors playing an indispensable role in "
                    "climate adaptation beyond wildlife conservation. Depressed freight cuttings and brick-lined "
                    "canal basins can be re-engineered as 'sponge corridors' that capture cloudburst runoff during "
                    "intense summer storms, relieving overburdened Victorian sewer networks. When combined with "
                    "continuous tree canopies that lower summer pavement temperatures by up to four degrees Celsius, "
                    "these reclaimed industrial arteries evolve from relics of a carbon-intensive past into "
                    "multifunctional shields for twenty-first-century cities."
                ),
            },
        ],
        "question_groups": [
            {
                "id": "p2-g1",
                "title": "Questions 14–19",
                "question_type": "matching_headings",
                "instructions": (
                    "Reading Passage 2 has six paragraphs, A–F. Choose the correct heading for each "
                    "paragraph from the list of headings (i–ix) below."
                ),
                "options": [
                    {"id": "i", "text": "Why linear habitats outperform isolated green spaces for wildlife movement"},
                    {"id": "ii", "text": "Unexpected biodiversity flourishing on nutrient-poor industrial ground"},
                    {"id": "iii", "text": "A historical timeline of nineteenth-century canal engineering"},
                    {"id": "iv", "text": "Designing visible signs of stewardship to build public support"},
                    {"id": "v", "text": "Biological strategies to manage toxic soil without costly excavation"},
                    {"id": "vi", "text": "Why municipal parks require heavier nitrogen fertilization"},
                    {"id": "vii", "text": "Unintended housing affordability pressures created by flagship green corridors"},
                    {"id": "viii", "text": "Repurposing former transport channels to mitigate extreme weather"},
                    {"id": "ix", "text": "Evidence that migratory birds avoid urban canal basins"},
                ],
                "question_numbers": [14, 15, 16, 17, 18, 19],
            },
            {
                "id": "p2-g2",
                "title": "Questions 20–23",
                "question_type": "matching_features",
                "instructions": (
                    "Look at the following findings and proposals (Questions 20–23) and the list of researchers "
                    "below. Match each statement with the correct researcher, A, B, C, or D. "
                    "NB: You may use any letter more than once."
                ),
                "options": [
                    {"id": "A", "text": "Dr. Clara Lindholm"},
                    {"id": "B", "text": "Mateo Alvarez"},
                    {"id": "C", "text": "Dr. Hannah Okafor"},
                    {"id": "D", "text": "Prof. Kenji Takahashi"},
                ],
                "question_numbers": [20, 21, 22, 23],
            },
            {
                "id": "p2-g3",
                "title": "Questions 24–26",
                "question_type": "summary_completion",
                "instructions": (
                    "Complete the summary below. Choose NO MORE THAN TWO WORDS from the passage for each answer."
                ),
                "word_limit": {
                    "max_words": 2,
                    "allow_number": False,
                    "label": "NO MORE THAN TWO WORDS",
                },
                "note_heading": "Climate Resilience Benefits of Reclaimed Corridors",
                "question_numbers": [24, 25, 26],
            },
        ],
    },
    {
        "index": 3,
        "title": "The Paradox of Cognitive Offloading",
        "subtitle": "Does outsourcing memory and navigation to digital tools weaken or liberate the human mind?",
        "topic": "Cognitive Psychology & Technology",
        "recommended_minutes": 20,
        "paragraphs": [
            {
                "id": "A",
                "text": (
                    "Every time a commuter glances at a turn-by-turn navigation screen or a researcher types a "
                    "reference query into a search bar, they participate in cognitive offloading—the deliberate use "
                    "of physical action or external tools to reduce internal mental demand. Critics in the popular "
                    "press frequently portray this habit as an unprecedented threat to human intellect, coining "
                    "alarmist phrases such as 'digital amnesia'. Yet cognitive scientists point out that relying on "
                    "external memory aids is neither novel nor inherently pathological. From knotted Andean quipu "
                    "cords and clay accounting tablets to printed almanacs and pocket notebooks, human civilization "
                    "has always expanded its cognitive reach by storing information outside the skull."
                ),
            },
            {
                "id": "B",
                "text": (
                    "What distinguishes contemporary digital offloading is not the principle itself, but its "
                    "frictionless speed and near-universal scope. When writing a note on paper, a learner must "
                    "actively filter, compress, and paraphrase incoming ideas, a process that naturally reinforces "
                    "neural encoding. By contrast, snapping a smartphone photograph of a lecture slide or saving an "
                    "entire webpage requires virtually zero semantic processing. Controlled laboratory studies by "
                    "cognitive psychologist Dr. Elena Rostova show that participants who know a computer folder "
                    "will reliably preserve a list of trivia facts recall significantly fewer items forty-eight "
                    "hours later than peers who expect the file to be erased—an effect researchers call 'transactive "
                    "memory shifting', where the brain remembers *where* to retrieve data rather than the data itself."
                ),
            },
            {
                "id": "C",
                "text": (
                    "Spatial navigation offers the clearest window into how habitual offloading alters neural "
                    "plasticity. In a longitudinal study of urban drivers, neuroscientists compared individuals who "
                    "navigated unfamiliar districts using paper street maps against those guided exclusively by "
                    "satellite voice prompts. The voice-guided group reached destinations slightly faster on their "
                    "first attempt, but performed markedly worse when asked to sketch a mental layout of the "
                    "neighbourhood or identify alternative routes after a simulated road closure. Functional MRI "
                    "scans revealed markedly lower activity in the hippocampus—the brain structure responsible for "
                    "building flexible cognitive maps—whenever participants passively obeyed turn-by-turn arrows."
                ),
            },
            {
                "id": "D",
                "text": (
                    "Even so, interpreting these findings as evidence of general mental decline commits a serious "
                    "analytical error. The same laboratory experiments reveal a compelling upside: freeing working "
                    "memory from rote retention leaves substantially greater attentional bandwidth for higher-order "
                    "synthesis, creative problem-solving, and error detection. In a 2024 clinical simulation involving "
                    "emergency-room nurses, teams allowed to offload medication dosage tables onto structured "
                    "digital checklists caught twenty-nine percent more subtle drug-interaction anomalies than teams "
                    "relying solely on memorized formulas. Offloading, in other words, trades narrow recall for "
                    "broader executive oversight."
                ),
            },
            {
                "id": "E",
                "text": (
                    "The real vulnerability arises when people misjudge the boundary between what resides in their "
                    "own understanding and what resides on a connected server. Psychologists describe this distortion "
                    "as 'metacognitive inflation': after answering several trivia questions with the help of rapid "
                    "web searches, volunteers routinely rate their unassisted general knowledge significantly higher "
                    "than control groups who answered without internet access, even on unrelated topics they never "
                    "looked up. When learners mistake instant access for genuine mastery, they stop practising the "
                    "effortful retrieval required to construct durable conceptual frameworks."
                ),
            },
            {
                "id": "F",
                "text": (
                    "Educational theorists therefore argue that the goal should never be a nostalgic ban on digital "
                    "aids, which would leave graduates ill-prepared for modern scientific and professional work. "
                    "Instead, curricula must teach 'strategic offloading'—the judgment to know which foundational "
                    "principles belong in rapid internal memory and which voluminous details belong in external "
                    "databases. Just as a skilled structural engineer relies on finite-element software for complex "
                    "load matrices while maintaining an intuitive grasp of physical scale to spot an absurd decimal "
                    "error, twenty-first-century thinkers need internal mental models strong enough to audit the "
                    "tools they depend upon."
                ),
            },
            {
                "id": "G",
                "text": (
                    "Ultimately, the paradox of cognitive offloading is resolved when we view intelligence not as a "
                    "sealed vault of memorized facts, but as a dynamic partnership between biological cognition and "
                    "cultural instruments. External tools neither automatically diminish nor automatically elevate "
                    "human thought. When deployed passively as substitutes for attention, they hollow out spatial "
                    "awareness and encourage illusions of competence; when wielded deliberately after core schemas "
                    "have been internalized, they allow human minds to tackle problems far beyond the limits of "
                    "unaided biology."
                ),
            },
        ],
        "question_groups": [
            {
                "id": "p3-g1",
                "title": "Questions 27–30",
                "question_type": "mcq_single",
                "instructions": "Choose the correct letter, A, B, C, or D.",
                "question_numbers": [27, 28, 29, 30],
            },
            {
                "id": "p3-g2",
                "title": "Questions 31–35",
                "question_type": "ynng",
                "instructions": (
                    "Do the following statements agree with the views of the writer in Reading Passage 3? "
                    "Choose YES if the statement agrees with the views of the writer, NO if the statement "
                    "contradicts the views of the writer, or NOT GIVEN if it is impossible to say what the "
                    "writer thinks about this."
                ),
                "question_numbers": [31, 32, 33, 34, 35],
            },
            {
                "id": "p3-g3",
                "title": "Questions 36–38",
                "question_type": "matching_sentence_endings",
                "instructions": (
                    "Complete each sentence with the correct ending, A–F, below."
                ),
                "options": [
                    {"id": "A", "text": "can spot implausible computational outputs using internalized intuition."},
                    {"id": "B", "text": "exhibit reduced hippocampal engagement during route guidance."},
                    {"id": "C", "text": "consistently underestimate their own ability to memorize technical vocabulary."},
                    {"id": "D", "text": "retain fewer raw facts when they trust a computer to store them reliably."},
                    {"id": "E", "text": "should prohibit students from consulting digital databases during university exams."},
                    {"id": "F", "text": "outperformed map readers when rerouting around unexpected street closures."},
                ],
                "question_numbers": [36, 37, 38],
            },
            {
                "id": "p3-g4",
                "title": "Questions 39–40",
                "question_type": "short_answer",
                "instructions": (
                    "Answer the questions below. Choose NO MORE THAN TWO WORDS AND/OR A NUMBER from the "
                    "passage for each answer."
                ),
                "word_limit": {
                    "max_words": 2,
                    "allow_number": True,
                    "max_numbers": 1,
                    "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER",
                },
                "question_numbers": [39, 40],
            },
        ],
    },
]


QUESTIONS: list[dict[str, Any]] = [
    # ==================== PASSAGE 1: Q1–Q6 (TFNG) ====================
    {
        "id": "p1-q01",
        "passage_index": 1,
        "question_number": 1,
        "question_type": "tfng",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "p1-g1",
            "prompt": "Excavations at Nendrum Monastery showed that tidal mills existed in northwestern Europe earlier than historians had previously believed.",
        },
        "answer_key": {"accepted": ["TRUE"]},
        "evidence_span": {
            "paragraph_id": "A",
            "quote": "pushing the documented origins of tidal milling in northwestern Europe nearly three centuries earlier than historians once assumed.",
            "distractor_note": "'earlier than historians once assumed' directly paraphrases 'earlier than historians had previously believed'.",
        },
    },
    {
        "id": "p1-q02",
        "passage_index": 1,
        "question_number": 2,
        "question_type": "tfng",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "p1-g1",
            "prompt": "Inland watermills were less affected by seasonal weather extremes than coastal tidal mills.",
        },
        "answer_key": {"accepted": ["FALSE"]},
        "evidence_span": {
            "paragraph_id": "A",
            "quote": "Unlike inland watermills, which frequently stalled during summer droughts or froze solid in harsh winters, tidal installations drew upon saline estuaries that remained ice-free",
            "distractor_note": "Comparative reversal trap: inland watermills were MORE affected by droughts and winter freezes, not less.",
        },
    },
    {
        "id": "p1-q03",
        "passage_index": 1,
        "question_number": 3,
        "question_type": "tfng",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g1",
            "prompt": "Millers had to manually pull shut the wooden flap gates once the tide reached its highest point.",
        },
        "answer_key": {"accepted": ["FALSE"]},
        "evidence_span": {
            "paragraph_id": "B",
            "quote": "Once the tide reached its peak and began to ebb, the reversing water pressure forced those same gates tightly shut",
            "distractor_note": "The gates closed automatically due to reversing water pressure, contradicting 'manually pull shut'.",
        },
    },
    {
        "id": "p1-q04",
        "passage_index": 1,
        "question_number": 4,
        "question_type": "tfng",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g1",
            "prompt": "Tidal millers in Suffolk were paid higher wages than millers in Brittany to compensate for irregular night shifts.",
        },
        "answer_key": {"accepted": ["NOT GIVEN"]},
        "evidence_span": {
            "paragraph_id": "C",
            "quote": "In coastal Suffolk and Brittany, families routinely began grinding grain at three in the morning during one week and late in the afternoon a fortnight later.",
            "distractor_note": "Both Suffolk and Brittany are mentioned for shifting work hours, but wages are never compared or mentioned (classic NOT GIVEN trap).",
        },
    },
    {
        "id": "p1-q05",
        "passage_index": 1,
        "question_number": 5,
        "question_type": "tfng",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g1",
            "prompt": "Tidal mills were exclusively used for grinding grain throughout the eighteenth century.",
        },
        "answer_key": {"accepted": ["FALSE"]},
        "evidence_span": {
            "paragraph_id": "E",
            "quote": "Although grain milling remained their primary function, ingenious entrepreneurs adapted tidal power to saw timber, crush mineral ore, full woollen cloth, and even pump municipal drinking water",
            "distractor_note": "Extreme qualifier trap ('exclusively'): grain milling was primary, not exclusive.",
        },
    },
    {
        "id": "p1-q06",
        "passage_index": 1,
        "question_number": 6,
        "question_type": "tfng",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p1-g1",
            "prompt": "Historical Victorian logbooks from tidal estuaries remain useful to contemporary marine energy engineers.",
        },
        "answer_key": {"accepted": ["TRUE"]},
        "evidence_span": {
            "paragraph_id": "G",
            "quote": "marine engineers investigating tidal range lagoons have revisited historic mill records with renewed appreciation. Detailed Victorian logbooks from the Rance estuary and the Severn basin preserve multi-decade observations",
            "distractor_note": "'revisited historic mill records with renewed appreciation' confirms continued usefulness.",
        },
    },
    # ==================== PASSAGE 1: Q7–Q13 (Note Completion, ONE WORD ONLY) ====================
    {
        "id": "p1-q07",
        "passage_index": 1,
        "question_number": 7,
        "question_type": "note_table_flowchart_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "A dam built across a coastal creek formed a water storage basin called a ________.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["millpond"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "B",
            "quote": "constructed an earthen or masonry dam across a narrow tidal creek to create an impounded reservoir known as a millpond.",
            "distractor_note": "Requires exact single-word noun 'millpond' (not 'impounded reservoir', which breaks ONE WORD ONLY).",
        },
    },
    {
        "id": "p1-q08",
        "passage_index": 1,
        "question_number": 8,
        "question_type": "note_table_flowchart_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "Because lunar cycles drift daily, merchants timed ________ deliveries to coincide with high tide.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["barge"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "C",
            "quote": "allowed coastal merchants to coordinate barge deliveries with high water",
            "distractor_note": "Check exact collocation before 'deliveries': 'barge' (not 'cargo vessels', which is two words and ungrammatical before 'deliveries').",
        },
    },
    {
        "id": "p1-q09",
        "passage_index": 1,
        "question_number": 9,
        "question_type": "note_table_flowchart_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "Opening bottom culverts at low tide cleared out built-up ________ from the pond floor.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["sediment", "mud"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "opening bottom culverts at dead low tide so the rushing outflow swept accumulated sediment back out to sea.",
            "distractor_note": "'accumulated' paraphrases 'built-up'; 'sediment' (or 'mud') fits ONE WORD ONLY.",
        },
    },
    {
        "id": "p1-q10",
        "passage_index": 1,
        "question_number": 10,
        "question_type": "note_table_flowchart_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "Underwater oak structures were damaged by marine molluscs known as ________.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["shipworms"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "Submerged oak pilings, meanwhile, were vulnerable to shipworms—molluscs capable of honeycombing untreated wood",
            "distractor_note": "'Submerged' paraphrases 'underwater'; plural noun 'shipworms' matches 'molluscs'.",
        },
    },
    {
        "id": "p1-q11",
        "passage_index": 1,
        "question_number": 11,
        "question_type": "note_table_flowchart_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "Some builders protected wooden frames by covering them in ________ sheeting or scorching the wood.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["copper"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "prompting builders in Devon and Maine to sheath critical frames in copper sheeting or scorch the timber surface with fire.",
            "distractor_note": "'sheath' paraphrases 'covering'; avoid repeating 'sheeting' since it already follows the gap.",
        },
    },
    {
        "id": "p1-q12",
        "passage_index": 1,
        "question_number": 12,
        "question_type": "note_table_flowchart_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "Nineteenth-century steam mills gained an advantage by locating near urban ________ terminals.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["railway"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "Steam-powered roller mills could be sited next to urban railway terminals rather than remote estuaries",
            "distractor_note": "'sited next to' paraphrases 'locating near'; exact single word is 'railway'.",
        },
    },
    {
        "id": "p1-q13",
        "passage_index": 1,
        "question_number": 13,
        "question_type": "note_table_flowchart_completion",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p1-g2",
            "prompt": "Modern tidal barrages must balance energy generation with protecting intertidal ________ used by birds and fish.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["mudflats"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "paragraph_id": "G",
            "quote": "capturing predictable marine energy while preserving intertidal mudflats that sustain migratory shorebirds and juvenile fish.",
            "distractor_note": "'preserving' paraphrases 'protecting'; plural noun 'mudflats' sits immediately after 'intertidal'.",
        },
    },
    # ==================== PASSAGE 2: Q14–Q19 (Matching Headings) ====================
    {
        "id": "p2-q14",
        "passage_index": 2,
        "question_number": 14,
        "question_type": "matching_headings",
        "target_band": 6.5,
        "prompt_payload": {"group_id": "p2-g1", "prompt": "Paragraph A"},
        "answer_key": {"accepted": ["ii"]},
        "evidence_span": {
            "paragraph_id": "A",
            "quote": "undisturbed railway ballast and limestone quarry edges often harbour a higher diversity of native wildflowers and solitary bees than manicured civic parks half a kilometre away.",
            "distractor_note": "Heading (vi) is a keyword trap mentioning nitrogen—Paragraph A says low nitrogen helps rare flora rather than advocating fertilization.",
        },
    },
    {
        "id": "p2-q15",
        "passage_index": 2,
        "question_number": 15,
        "question_type": "matching_headings",
        "target_band": 6.5,
        "prompt_payload": {"group_id": "p2-g1", "prompt": "Paragraph B"},
        "answer_key": {"accepted": ["i"]},
        "evidence_span": {
            "paragraph_id": "B",
            "quote": "By contrast, continuous vegetated railway verges function as biological highways, enabling genetic exchange between peripheral woodlands and inner-city gardens.",
            "distractor_note": "Core contrast of Paragraph B is continuous corridors vs. isolated pocket parks.",
        },
    },
    {
        "id": "p2-q16",
        "passage_index": 2,
        "question_number": 16,
        "question_type": "matching_headings",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "p2-g1", "prompt": "Paragraph C"},
        "answer_key": {"accepted": ["v"]},
        "evidence_span": {
            "paragraph_id": "C",
            "quote": "Instead, Alvarez champions phytoremediation: planting willow thickets and Indian mustard cultivars that immobilize or gradually draw down soil toxins in situ",
            "distractor_note": "'Biological strategies' paraphrases phytoremediation with plants instead of costly landfill excavation.",
        },
    },
    {
        "id": "p2-q17",
        "passage_index": 2,
        "question_number": 17,
        "question_type": "matching_headings",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "p2-g1", "prompt": "Paragraph D"},
        "answer_key": {"accepted": ["iv"]},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "adding minimal 'cues to care'—such as crisp mown border strips along pathways, interpretive signage explaining seasonal meadow cycles, and timber benches—raised neighbourhood approval ratings dramatically",
            "distractor_note": "'visible signs of stewardship' paraphrases 'cues to care' (mown borders, signage, benches).",
        },
    },
    {
        "id": "p2-q18",
        "passage_index": 2,
        "question_number": 18,
        "question_type": "matching_headings",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "p2-g1", "prompt": "Paragraph E"},
        "answer_key": {"accepted": ["vii"]},
        "evidence_span": {
            "paragraph_id": "E",
            "quote": "Success in urban rewilding has also sparked an unintended real-estate phenomenon termed 'ecological gentrification'.",
            "distractor_note": "Paragraph E centers on rent spikes and displacement around flagship rail-park conversions.",
        },
    },
    {
        "id": "p2-q19",
        "passage_index": 2,
        "question_number": 19,
        "question_type": "matching_headings",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "p2-g1", "prompt": "Paragraph F"},
        "answer_key": {"accepted": ["viii"]},
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "Depressed freight cuttings and brick-lined canal basins can be re-engineered as 'sponge corridors' that capture cloudburst runoff during intense summer storms",
            "distractor_note": "Heading (iii) is a Victorian-keyword distractor; Paragraph F is forward-looking climate adaptation, not a canal history timeline.",
        },
    },
    # ==================== PASSAGE 2: Q20–Q23 (Matching Features) ====================
    {
        "id": "p2-q20",
        "passage_index": 2,
        "question_number": 20,
        "question_type": "matching_features",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p2-g2",
            "prompt": "Recommended pairing green corridor investments with housing protections from the earliest planning stage.",
        },
        "answer_key": {"accepted": ["D"]},
        "evidence_span": {
            "paragraph_id": "E",
            "quote": "Takahashi argues that green corridor projects must be paired from inception with community land trusts or rent-stabilized housing quotas",
            "distractor_note": "'from inception' paraphrases 'from the earliest planning stage' -> Prof. Kenji Takahashi (D).",
        },
    },
    {
        "id": "p2-q21",
        "passage_index": 2,
        "question_number": 21,
        "question_type": "matching_features",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p2-g2",
            "prompt": "Used animal tracking data to show that fragmented city parks fail to sustain wildlife populations.",
        },
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "paragraph_id": "B",
            "quote": "Dr. Clara Lindholm has demonstrated through GPS tracking of hedgehogs and nocturnal moths in Stockholm that isolated pocket parks act as demographic traps",
            "distractor_note": "'isolated pocket parks act as demographic traps' paraphrases 'fragmented city parks fail to sustain wildlife populations' -> Dr. Clara Lindholm (A).",
        },
    },
    {
        "id": "p2-q22",
        "passage_index": 2,
        "question_number": 22,
        "question_type": "matching_features",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p2-g2",
            "prompt": "Highlighted the high budgetary and emissions cost of removing polluted soil by truck.",
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "paragraph_id": "C",
            "quote": "Mateo Alvarez warns that excavating and trucking polluted earth to hazardous landfills can consume up to seventy percent of a city's green-space budget while generating substantial carbon emissions.",
            "distractor_note": "Directly attributed to Mateo Alvarez (B).",
        },
    },
    {
        "id": "p2-q23",
        "passage_index": 2,
        "question_number": 23,
        "question_type": "matching_features",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p2-g2",
            "prompt": "Found that residents sometimes mistook ecologically valuable unmown vegetation for poor maintenance.",
        },
        "answer_key": {"accepted": ["C"]},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "many long-term neighbours initially interpreted tall dry grass as municipal neglect or an invitation to illegal dumping.",
            "distractor_note": "'municipal neglect' paraphrases 'poor maintenance' -> Dr. Hannah Okafor (C).",
        },
    },
    # ==================== PASSAGE 2: Q24–Q26 (Summary Completion, NO MORE THAN TWO WORDS) ====================
    {
        "id": "p2-q24",
        "passage_index": 2,
        "question_number": 24,
        "question_type": "summary_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p2-g3",
            "prompt": "Former rail cuttings and canal basins can be adapted into ________ that absorb intense rainwater.",
            "word_limit": {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"},
        },
        "answer_key": {
            "accepted": ["sponge corridors"],
            "word_limit": {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"},
        },
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "Depressed freight cuttings and brick-lined canal basins can be re-engineered as 'sponge corridors' that capture cloudburst runoff",
            "distractor_note": "Exact two-word term 'sponge corridors' fits grammar and word limit.",
        },
    },
    {
        "id": "p2-q25",
        "passage_index": 2,
        "question_number": 25,
        "question_type": "summary_completion",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p2-g3",
            "prompt": "Capturing storm runoff reduces pressure on ageing Victorian ________.",
            "word_limit": {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"},
        },
        "answer_key": {
            "accepted": ["sewer networks"],
            "word_limit": {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"},
        },
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "relieving overburdened Victorian sewer networks.",
            "distractor_note": "'Victorian' already appears before the gap, so writing 'Victorian sewer networks' duplicates a word and violates NO MORE THAN TWO WORDS.",
        },
    },
    {
        "id": "p2-q26",
        "passage_index": 2,
        "question_number": 26,
        "question_type": "summary_completion",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p2-g3",
            "prompt": "Continuous ________ along these routes also help cool city pavements during hot summers.",
            "word_limit": {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"},
        },
        "answer_key": {
            "accepted": ["tree canopies"],
            "word_limit": {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"},
        },
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "When combined with continuous tree canopies that lower summer pavement temperatures by up to four degrees Celsius",
            "distractor_note": "Plural noun phrase 'tree canopies' agrees with the plural verb 'help' in the summary.",
        },
    },
    # ==================== PASSAGE 3: Q27–Q30 (MCQ Single) ====================
    {
        "id": "p3-q27",
        "passage_index": 3,
        "question_number": 27,
        "question_type": "mcq_single",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p3-g1",
            "prompt": "Why does the writer mention Andean quipu cords and clay accounting tablets in Paragraph A?",
            "options": [
                {"id": "A", "text": "To prove that ancient societies possessed superior human memory"},
                {"id": "B", "text": "To illustrate that externalizing mental tasks has deep historical precedent"},
                {"id": "C", "text": "To show that digital amnesia began during early trade civilizations"},
                {"id": "D", "text": "To argue that paper notebooks are more reliable than smartphones"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "paragraph_id": "A",
            "quote": "relying on external memory aids is neither novel nor inherently pathological. From knotted Andean quipu cords and clay accounting tablets to printed almanacs and pocket notebooks, human civilization has always expanded its cognitive reach",
            "distractor_note": "Options A, C, and D distort the author's point; the examples demonstrate long-standing historical continuity (B).",
        },
    },
    {
        "id": "p3-q28",
        "passage_index": 3,
        "question_number": 28,
        "question_type": "mcq_single",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p3-g1",
            "prompt": "According to Paragraph B, what is a key difference between handwritten note-taking and photographing a lecture slide?",
            "options": [
                {"id": "A", "text": "Photographs consume more mental energy to organize later"},
                {"id": "B", "text": "Handwritten notes encourage active mental processing that strengthens encoding"},
                {"id": "C", "text": "Slide photography helps students recall trivia better after forty-eight hours"},
                {"id": "D", "text": "Handwriting eliminates the need for transactive memory"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "paragraph_id": "B",
            "quote": "When writing a note on paper, a learner must actively filter, compress, and paraphrase incoming ideas, a process that naturally reinforces neural encoding.",
            "distractor_note": "Option B directly captures the contrast in semantic processing and neural encoding.",
        },
    },
    {
        "id": "p3-q29",
        "passage_index": 3,
        "question_number": 29,
        "question_type": "mcq_single",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g1",
            "prompt": "What did the 2024 clinical simulation with emergency-room nurses demonstrate?",
            "options": [
                {"id": "A", "text": "Memorizing dosage tables prevents nurses from working in teams"},
                {"id": "B", "text": "Digital checklists slowed down emergency decision-making"},
                {"id": "C", "text": "Offloading routine reference data improved detection of complex clinical risks"},
                {"id": "D", "text": "Nurses overestimated their pharmacological knowledge when using checklists"},
            ],
        },
        "answer_key": {"accepted": ["C"]},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "teams allowed to offload medication dosage tables onto structured digital checklists caught twenty-nine percent more subtle drug-interaction anomalies than teams relying solely on memorized formulas.",
            "distractor_note": "Option D mixes in a concept from Paragraph E (metacognitive inflation); Paragraph D specifically shows improved anomaly detection (C).",
        },
    },
    {
        "id": "p3-q30",
        "passage_index": 3,
        "question_number": 30,
        "question_type": "mcq_single",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g1",
            "prompt": "What does the writer mean by 'metacognitive inflation' in Paragraph E?",
            "options": [
                {"id": "A", "text": "Mistaking rapid access to online information for personal internal knowledge"},
                {"id": "B", "text": "Feeling overwhelmed by the volume of data stored on connected servers"},
                {"id": "C", "text": "Remembering website addresses more clearly than academic principles"},
                {"id": "D", "text": "Spending excessive study time on unrelated trivia topics"},
            ],
        },
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "paragraph_id": "E",
            "quote": "When learners mistake instant access for genuine mastery, they stop practising the effortful retrieval required to construct durable conceptual frameworks.",
            "distractor_note": "Option C describes transactive memory from Paragraph B, not metacognitive inflation in Paragraph E (A).",
        },
    },
    # ==================== PASSAGE 3: Q31–Q35 (YNNG) ====================
    {
        "id": "p3-q31",
        "passage_index": 3,
        "question_number": 31,
        "question_type": "ynng",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "p3-g2",
            "prompt": "Popular media warnings about 'digital amnesia' overlook the long history of human external memory aids.",
        },
        "answer_key": {"accepted": ["YES"]},
        "evidence_span": {
            "paragraph_id": "A",
            "quote": "Yet cognitive scientists point out that relying on external memory aids is neither novel nor inherently pathological.",
            "distractor_note": "The author explicitly endorses cognitive scientists' critique that popular press warnings treat an ancient habit as unprecedented.",
        },
    },
    {
        "id": "p3-q32",
        "passage_index": 3,
        "question_number": 32,
        "question_type": "ynng",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p3-g2",
            "prompt": "Reduced recall in laboratory offloading experiments proves that modern technology is causing overall cognitive decline.",
        },
        "answer_key": {"accepted": ["NO"]},
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "Even so, interpreting these findings as evidence of general mental decline commits a serious analytical error.",
            "distractor_note": "Direct contradiction: the writer calls that interpretation 'a serious analytical error'.",
        },
    },
    {
        "id": "p3-q33",
        "passage_index": 3,
        "question_number": 33,
        "question_type": "ynng",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p3-g2",
            "prompt": "Older adults are less susceptible to metacognitive inflation than university-aged search users.",
        },
        "answer_key": {"accepted": ["NOT GIVEN"]},
        "evidence_span": {
            "paragraph_id": "E",
            "quote": "volunteers routinely rate their unassisted general knowledge significantly higher than control groups who answered without internet access",
            "distractor_note": "Age groups are never compared in Paragraph E — classic NOT GIVEN comparison trap.",
        },
    },
    {
        "id": "p3-q34",
        "passage_index": 3,
        "question_number": 34,
        "question_type": "ynng",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g2",
            "prompt": "Schools and universities should ban digital reference tools so students preserve traditional memorization habits.",
        },
        "answer_key": {"accepted": ["NO"]},
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "Educational theorists therefore argue that the goal should never be a nostalgic ban on digital aids, which would leave graduates ill-prepared for modern scientific and professional work.",
            "distractor_note": "The writer directly rejects banning digital aids ('should never be a nostalgic ban').",
        },
    },
    {
        "id": "p3-q35",
        "passage_index": 3,
        "question_number": 35,
        "question_type": "ynng",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g2",
            "prompt": "Digital tools are most beneficial when learners already possess solid internal mental frameworks.",
        },
        "answer_key": {"accepted": ["YES"]},
        "evidence_span": {
            "paragraph_id": "G",
            "quote": "when wielded deliberately after core schemas have been internalized, they allow human minds to tackle problems far beyond the limits of unaided biology.",
            "distractor_note": "'after core schemas have been internalized' directly matches 'already possess solid internal mental frameworks'.",
        },
    },
    # ==================== PASSAGE 3: Q36–Q38 (Matching Sentence Endings) ====================
    {
        "id": "p3-q36",
        "passage_index": 3,
        "question_number": 36,
        "question_type": "matching_sentence_endings",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p3-g3",
            "prompt": "Participants in Dr. Elena Rostova's experiments",
        },
        "answer_key": {"accepted": ["D"]},
        "evidence_span": {
            "paragraph_id": "B",
            "quote": "participants who know a computer folder will reliably preserve a list of trivia facts recall significantly fewer items forty-eight hours later",
            "distractor_note": "Matches ending D ('retain fewer raw facts when they trust a computer to store them reliably').",
        },
    },
    {
        "id": "p3-q37",
        "passage_index": 3,
        "question_number": 37,
        "question_type": "matching_sentence_endings",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g3",
            "prompt": "Urban drivers who rely solely on voice-prompted satellite navigation",
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "paragraph_id": "C",
            "quote": "Functional MRI scans revealed markedly lower activity in the hippocampus—the brain structure responsible for building flexible cognitive maps—whenever participants passively obeyed turn-by-turn arrows.",
            "distractor_note": "Ending F reverses the study result (they performed worse on road closures); ending B matches reduced hippocampal activity.",
        },
    },
    {
        "id": "p3-q38",
        "passage_index": 3,
        "question_number": 38,
        "question_type": "matching_sentence_endings",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g3",
            "prompt": "Experienced structural engineers using load-calculation software",
        },
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "paragraph_id": "F",
            "quote": "a skilled structural engineer relies on finite-element software for complex load matrices while maintaining an intuitive grasp of physical scale to spot an absurd decimal error",
            "distractor_note": "'spot an absurd decimal error' paraphrases 'spot implausible computational outputs' (A).",
        },
    },
    # ==================== PASSAGE 3: Q39–Q40 (Short Answer, NO MORE THAN TWO WORDS AND/OR A NUMBER) ====================
    {
        "id": "p3-q39",
        "passage_index": 3,
        "question_number": 39,
        "question_type": "short_answer",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "p3-g4",
            "prompt": "Which specific brain region showed reduced activity during passive turn-by-turn navigation?",
            "word_limit": {
                "max_words": 2,
                "allow_number": True,
                "max_numbers": 1,
                "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER",
            },
        },
        "answer_key": {
            "accepted": ["(the) hippocampus"],
            "word_limit": {
                "max_words": 2,
                "allow_number": True,
                "max_numbers": 1,
                "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER",
            },
        },
        "evidence_span": {
            "paragraph_id": "C",
            "quote": "Functional MRI scans revealed markedly lower activity in the hippocampus",
            "distractor_note": "Both 'hippocampus' and 'the hippocampus' satisfy NO MORE THAN TWO WORDS.",
        },
    },
    {
        "id": "p3-q40",
        "passage_index": 3,
        "question_number": 40,
        "question_type": "short_answer",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "p3-g4",
            "prompt": "By what percentage did checklist-assisted nursing teams outperform memory-only teams in catching subtle drug-interaction anomalies?",
            "word_limit": {
                "max_words": 2,
                "allow_number": True,
                "max_numbers": 1,
                "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER",
            },
        },
        "answer_key": {
            "accepted": ["29%", "twenty-nine percent", "29 percent"],
            "word_limit": {
                "max_words": 2,
                "allow_number": True,
                "max_numbers": 1,
                "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER",
            },
        },
        "evidence_span": {
            "paragraph_id": "D",
            "quote": "caught twenty-nine percent more subtle drug-interaction anomalies than teams relying solely on memorized formulas.",
            "distractor_note": "Tests numeric equivalence ('29%', '29 percent', 'twenty-nine percent') and hyphenated word counting ('twenty-nine' = 1 word).",
        },
    },
]


def seed_strategy_notes(db: Session, notes_dir: Path | None = None) -> int:
    """Load curated and parsed IELTS Advantage notes from data/notes/*.json into knowledge_concepts."""
    target_dir = notes_dir or get_settings().notes_dir
    if not target_dir.exists():
        return 0

    inserted = 0
    for json_file in sorted(target_dir.glob("*.json")):
        raw = json.loads(json_file.read_text(encoding="utf-8"))
        entries = raw if isinstance(raw, list) else [raw]
        for entry in entries:
            note = StrategyNote.model_validate(entry)
            existing = (
                db.query(KnowledgeConcept)
                .filter(KnowledgeConcept.source_video_id == note.source_video_id)
                .first()
            )
            if existing:
                continue
            concept = KnowledgeConcept(
                module=note.module,
                question_type=note.question_type,
                source_type="ielts_advantage",
                source_video_id=note.source_video_id,
                source_url=note.source_url,
                title=note.title,
                payload_json=note.model_dump(),
                summary_md=note.to_markdown(),
            )
            db.add(concept)
            inserted += 1

    db.commit()
    return inserted


def seed_reading_mock(db: Session) -> bool:
    """Seed the original 40-question Academic Reading mock test idempotently."""
    existing = db.get(ReadingTest, READING_TEST_ID)
    if existing is not None:
        return False

    test = ReadingTest(
        id=READING_TEST_ID,
        title="IELTS Academic Reading Practice Test 01",
        subtitle=(
            "Original 3-passage calibrated mock covering T/F/NG, Note Completion, Matching Headings, "
            "Matching Features, Summary Completion, MCQ, Y/N/NG, Matching Sentence Endings, and Short Answer."
        ),
        difficulty_label="Band 6.0–8.5",
        duration_minutes=60,
        passages_json=PASSAGES,
        verified=True,
    )
    db.add(test)

    for q in QUESTIONS:
        db.add(
            QuestionItem(
                id=q["id"],
                test_id=READING_TEST_ID,
                passage_index=q["passage_index"],
                question_number=q["question_number"],
                module="reading",
                question_type=q["question_type"],
                target_band=q["target_band"],
                prompt_payload=q["prompt_payload"],
                answer_key=q["answer_key"],
                evidence_span=q["evidence_span"],
                verified=True,
            )
        )

    db.commit()
    return True


def seed_reading_drill_bank(db: Session) -> int:
    """Seed all 30 original Academic Reading single-passage drill passages idempotently."""
    from backend.app.seeds.reading_bank_p1 import P1_DRILLS
    from backend.app.seeds.reading_bank_p2 import P2_DRILLS
    from backend.app.seeds.reading_bank_p3 import P3_DRILLS

    all_drills = P1_DRILLS + P2_DRILLS + P3_DRILLS
    added = 0
    for drill in all_drills:
        if db.get(ReadingTest, drill["id"]) is not None:
            continue
        db.add(
            ReadingTest(
                id=drill["id"],
                title=drill["title"],
                subtitle=drill["subtitle"],
                difficulty_label=drill["difficulty_label"],
                duration_minutes=drill["duration_minutes"],
                is_drill_bank=True,
                drill_slot=drill["drill_slot"],
                passages_json=drill["passages"],
                verified=True,
            )
        )
        for q in drill["questions"]:
            db.add(
                QuestionItem(
                    id=q["id"],
                    test_id=drill["id"],
                    passage_index=q["passage_index"],
                    question_number=q["question_number"],
                    module="reading",
                    question_type=q["question_type"],
                    target_band=q["target_band"],
                    prompt_payload=q["prompt_payload"],
                    answer_key=q["answer_key"],
                    evidence_span=q["evidence_span"],
                    verified=True,
                )
            )
        added += 1

    db.commit()
    return added


def run_all_seeds(db: Session) -> dict[str, int | bool]:
    """Run all idempotent Milestone 1 + Milestone 2 database seeds."""
    from backend.app.seeds.listening_seed import seed_listening_mock

    notes_added = seed_strategy_notes(db)
    test_added = seed_reading_mock(db)
    drills_added = seed_reading_drill_bank(db)
    listening_added = seed_listening_mock(db)
    return {
        "notes_added": notes_added,
        "reading_test_added": test_added,
        "reading_drills_added": drills_added,
        "listening_test_added": listening_added,
    }
