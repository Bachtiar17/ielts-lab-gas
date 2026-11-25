"""Original Academic Reading Drill Bank — Slot 2 (10 Passage-2 style drills).

Each drill features 4 analytical paragraphs (A-D) with Matching Headings (Q1-Q4)
and Summary Completion (NO MORE THAN TWO WORDS, Q5-Q6).
"""

from __future__ import annotations

from typing import Any


def _make_p2_drill(
    slug: str,
    title: str,
    subtitle: str,
    topic: str,
    paragraphs: list[tuple[str, str]],
    headings: list[tuple[str, str]],
    heading_answers: list[tuple[str, str, str, str]],  # (para_id, correct_roman, quote, note)
    summary_items: list[tuple[str, list[str], str, str, str]],
) -> dict[str, Any]:
    wl = {"max_words": 2, "allow_number": False, "label": "NO MORE THAN TWO WORDS"}
    questions: list[dict[str, Any]] = []
    for idx, (pid, roman, quote, note) in enumerate(heading_answers, start=1):
        questions.append(
            {
                "id": f"{slug}-q{idx:02d}",
                "passage_index": 1,
                "question_number": idx,
                "question_type": "matching_headings",
                "target_band": 7.0,
                "prompt_payload": {"group_id": f"{slug}-g1", "prompt": f"Paragraph {pid}"},
                "answer_key": {"accepted": [roman]},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    for offset, (prompt, accepted, pid, quote, note) in enumerate(summary_items, start=5):
        questions.append(
            {
                "id": f"{slug}-q{offset:02d}",
                "passage_index": 1,
                "question_number": offset,
                "question_type": "summary_completion",
                "target_band": 7.0,
                "prompt_payload": {"group_id": f"{slug}-g2", "prompt": prompt, "word_limit": wl},
                "answer_key": {"accepted": accepted, "word_limit": wl},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    return {
        "id": slug,
        "title": title,
        "subtitle": subtitle,
        "difficulty_label": "Passage 2 · Band 6.5–7.5",
        "duration_minutes": 18,
        "drill_slot": 2,
        "passages": [
            {
                "index": 1,
                "title": title,
                "subtitle": subtitle,
                "topic": topic,
                "recommended_minutes": 18,
                "paragraphs": [{"id": pid, "text": txt} for pid, txt in paragraphs],
                "question_groups": [
                    {
                        "id": f"{slug}-g1",
                        "title": "Questions 1–4",
                        "question_type": "matching_headings",
                        "instructions": "Choose the correct heading for each paragraph (A–D) from the list below.",
                        "options": [{"id": hid, "text": htxt} for hid, htxt in headings],
                        "question_numbers": [1, 2, 3, 4],
                    },
                    {
                        "id": f"{slug}-g2",
                        "title": "Questions 5–6",
                        "question_type": "summary_completion",
                        "instructions": "Complete the summary below. Choose NO MORE THAN TWO WORDS from the passage for each answer.",
                        "word_limit": wl,
                        "question_numbers": [5, 6],
                    },
                ],
            }
        ],
        "questions": questions,
    }


P2_DRILLS: list[dict[str, Any]] = [
    _make_p2_drill(
        "drill-p2-01",
        "Mycelium Composites in Circular Construction",
        "Growing structural insulation panels from agricultural straw and fungal root networks",
        "Materials Science",
        [
            ("A", "Conventional foam insulation derived from petrochemicals poses a stubborn end-of-life burden because expanded polystyrene resists microbial decay for centuries. Seeking biodegradable alternatives, materials scientists have turned to mycelium—the branching subterranean root web of fungi—which binds loose agricultural residues such as hemp hurds or rice husks into rigid lightweight boards."),
            ("B", "Manufacturing begins by sterilizing chopped crop waste and inoculating it with fungal spores inside reusable moulds. Over five to seven days in humid darkened chambers, thread-like hyphae colonize the substrate and secrete natural chitin polymers that glue particles together. Once the panel reaches target density, gentle kiln baking deactivates the organism so the finished block neither sprouts mushrooms nor releases spores indoors."),
            ("C", "Laboratory fire and thermal trials show that baked mycelium boards insulate comparably to mineral wool while naturally charring rather than dripping flaming resin when exposed to heat. However, their low compressive strength currently prevents builders from using pure mycelium panels in load-bearing skyscrapers, limiting deployment to acoustic partitions and interior wall cores."),
            ("D", "Scaling the industry hinges on regional supply chains rather than centralized mega-factories. Because dry crop straw is bulky and uneconomical to haul long distances, economists predict a distributed model in which small bio-fabrication hubs operate beside grain mills, converting seasonal husks into local building stock."),
        ],
        [
            ("i", "Thermal strengths alongside current structural limits"),
            ("ii", "Why petrochemical foams prompted interest in fungal binders"),
            ("iii", "Step-by-step cultivation and heat stabilization of panels"),
            ("iv", "How bulky raw materials favour decentralized regional production"),
            ("v", "Legal bans on mushroom farming near urban apartments"),
            ("vi", "Evidence that kiln baking lowers acoustic absorption"),
        ],
        [
            ("A", "ii", "expanded polystyrene resists microbial decay for centuries. Seeking biodegradable alternatives, materials scientists have turned to mycelium", "Sets up the environmental problem motivating fungal composites."),
            ("B", "iii", "Once the panel reaches target density, gentle kiln baking deactivates the organism so the finished block neither sprouts mushrooms nor releases spores indoors.", "Walks through the cultivation and heat-stabilization workflow."),
            ("C", "i", "However, their low compressive strength currently prevents builders from using pure mycelium panels in load-bearing skyscrapers, limiting deployment to acoustic partitions and interior wall cores.", "Balances advantages with structural limits."),
            ("D", "iv", "Because dry crop straw is bulky and uneconomical to haul long distances, economists predict a distributed model", "Explains decentralized regional production."),
        ],
        [
            ("During growth, fungal hyphae secrete natural ________ that bind loose crop residues together.", ["chitin polymers"], "B", "secrete natural chitin polymers that glue particles together.", "Exact two-word noun phrase."),
            ("Because pure panels lack high ________, they are currently used mainly for interior partitions.", ["compressive strength"], "C", "their low compressive strength currently prevents builders from using pure mycelium panels", "Exact two-word engineering property."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-02",
        "Acoustic Ecology of Coral Reefs",
        "Underwater soundscapes guide larval fish back to healthy marine habitats",
        "Marine Biology",
        [
            ("A", "To casual snorkellers, a tropical coral reef appears primarily visual—a mosaic of staghorn branches and darting parrotfish. Hydrophone recordings reveal a very different reality: healthy reefs rank among the loudest biological environments in the ocean, crackling continuously with snapping shrimp claws, damselfish grunts, and urchin grazing."),
            ("B", "Marine ecologists discovered that this reef chorus serves as an acoustic beacon for microscopic fish larvae drifting kilometres offshore in open water. As larvae mature and prepare to settle, tiny calcium ear stones called otoliths detect particle motion carried by low-frequency reef sounds, steering juvenile recruits toward thriving coral cover rather than barren sand."),
            ("C", "When thermal bleaching kills living coral polyps and smothers reefs in algae, the biological soundscape falls eerily quiet. Without acoustic cues, passing larvae fail to settle, trapping degraded reefs in a self-reinforcing decline where fewer grazing fish allow even thicker algal mats to spread."),
            ("D", "In experimental trials on Australia's Great Barrier Reef, researchers placed underwater loudspeakers on dead coral patches to broadcast recordings of healthy reef choruses—a method called acoustic enrichment. Within six weeks, twice as many juvenile damselfish settled on sound-enriched rubble compared with silent control sites, demonstrating that sound playback can jump-start ecological recovery alongside coral transplantation."),
        ],
        [
            ("i", "How silence locks bleached reefs into a downward spiral"),
            ("ii", "Revealing the hidden acoustic richness of healthy coral habitats"),
            ("iii", "Using underwater loudspeakers to accelerate reef restoration"),
            ("iv", "How drifting juvenile fish navigate toward reefs by ear"),
            ("v", "Why snapping shrimp migrate away from coastal lagoons"),
            ("vi", "Comparing hydrophone costs across Pacific research stations"),
        ],
        [
            ("A", "ii", "healthy reefs rank among the loudest biological environments in the ocean, crackling continuously", "Contrasts visual assumptions with acoustic richness."),
            ("B", "iv", "tiny calcium ear stones called otoliths detect particle motion carried by low-frequency reef sounds, steering juvenile recruits", "Explains acoustic navigation by larvae."),
            ("C", "i", "the biological soundscape falls eerily quiet. Without acoustic cues, passing larvae fail to settle, trapping degraded reefs in a self-reinforcing decline", "Explains the silent feedback loop."),
            ("D", "iii", "placed underwater loudspeakers on dead coral patches to broadcast recordings of healthy reef choruses—a method called acoustic enrichment.", "Describes loudspeaker playback trials."),
        ],
        [
            ("Fish larvae sense reef vibrations using tiny calcium structures called ________.", ["otoliths", "ear stones"], "B", "tiny calcium ear stones called otoliths detect particle motion", "Exact anatomical term."),
            ("Broadcasting healthy reef recordings on degraded sites is known as ________.", ["acoustic enrichment"], "D", "a method called acoustic enrichment.", "Exact two-word term."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-03",
        "The Urban Heat Island and Cool Pavements",
        "Reflective road coatings reshape street-level microclimates in warming cities",
        "Urban Climatology",
        [
            ("A", "Dark asphalt absorbs up to ninety percent of incoming solar radiation, storing heat throughout the afternoon and releasing it slowly after sunset. Consequently, densely paved metropolitan cores often register nocturnal air temperatures four to six degrees Celsius warmer than surrounding farmland—a phenomenon known as the urban heat island effect."),
            ("B", "Seeking rapid relief without tearing up existing roadbeds, several sun-belt municipalities have applied titanium-dioxide reflective sealants that raise surface albedo. Infrared drone surveys in Phoenix confirmed that coated residential streets stayed nearly six degrees cooler at noon than adjacent blacktop, reducing thermal wear on asphalt binders."),
            ("C", "Yet pedestrian thermal-comfort studies revealed an unexpected trade-off. When light-coloured pavements bounce shortwave solar energy upward at midday, walkers standing on unshaded boulevards actually experience higher mean radiant heat on their skin unless street trees intercept the reflected glare."),
            ("D", "Climatologists therefore advise deploying reflective coatings selectively—prioritizing sunlit rooftops, bus depots, and tree-lined residential lanes—while pairing open plazas with permeable grass pavers and shade canopies that cool both ground and pedestrians simultaneously."),
        ],
        [
            ("i", "Why reflective streets can unintentionally warm exposed pedestrians"),
            ("ii", "Targeted deployment strategies combining coatings with shade"),
            ("iii", "Measured midday surface cooling from reflective sealants"),
            ("iv", "How dark road surfaces create elevated city night temperatures"),
            ("v", "Legal disputes over municipal asphalt warranties"),
            ("vi", "Why suburban farms retain more heat than downtown blocks"),
        ],
        [
            ("A", "iv", "Consequently, densely paved metropolitan cores often register nocturnal air temperatures four to six degrees Celsius warmer than surrounding farmland—a phenomenon known as the urban heat island effect.", "Explains the physical mechanism of urban heat islands."),
            ("B", "iii", "coated residential streets stayed nearly six degrees cooler at noon than adjacent blacktop", "Reports measured cooling results."),
            ("C", "i", "walkers standing on unshaded boulevards actually experience higher mean radiant heat on their skin", "Highlights the pedestrian glare trade-off."),
            ("D", "ii", "advise deploying reflective coatings selectively—prioritizing sunlit rooftops, bus depots, and tree-lined residential lanes", "Recommends targeted paired deployment."),
        ],
        [
            ("Reflective sealants containing titanium dioxide increase a road's ________.", ["surface albedo", "albedo"], "B", "applied titanium-dioxide reflective sealants that raise surface albedo.", "Exact two-word physical property."),
            ("Planners recommend pairing open plazas with shade canopies and ________.", ["permeable grass", "grass pavers"], "D", "pairing open plazas with permeable grass pavers and shade canopies", "Fits NO MORE THAN TWO WORDS."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-04",
        "Boreal Peatlands: Earth's Hidden Carbon Vaults",
        "Waterlogged northern bogs store twice as much carbon as all global forests",
        "Earth Science",
        [
            ("A", "Covering barely three percent of Earth's land surface, northern peatlands hold more than twice the carbon locked inside every tropical and temperate forest combined. In cold waterlogged bogs, oxygen levels stay so low that dead sphagnum moss decays at a glacial pace, accumulating metre-deep organic layers over ten thousand years."),
            ("B", "That ancient equilibrium unravels quickly whenever drainage ditches are cut for timber plantations or peat-fuel extraction. Once the water table drops, air penetrates dry peat fibres, activating aerobic microbes that oxidize millennia of stored carbon back into atmospheric carbon dioxide within decades."),
            ("C", "Drained peatlands also pose an acute wildfire hazard. Unlike surface brush fires extinguished by rain, smouldering peat fires burn underground for months, releasing dense particulate plumes and surviving beneath winter snowpacks only to reignite in spring as so-called zombie fires."),
            ("D", "Rewetting campaigns across Scotland, Finland, and Belarus are now blocking legacy drainage channels with wooden dams and sphagnum plugs. Satellite flux towers confirm that raising water tables back near the surface halts carbon oxidation rapidly, though temporary spikes in methane emissions require careful hydrological monitoring."),
        ],
        [
            ("i", "How draining bogs triggers rapid microbial carbon release"),
            ("ii", "Restoring water tables and tracking short-term gas trade-offs"),
            ("iii", "Why oxygen-starved mosses accumulate vast carbon reserves"),
            ("iv", "Persistent underground combustion risks in dried peat"),
            ("v", "New industrial uses for sphagnum moss in textiles"),
            ("vi", "Why tropical rainforests outpace peatlands in soil carbon"),
        ],
        [
            ("A", "iii", "oxygen levels stay so low that dead sphagnum moss decays at a glacial pace, accumulating metre-deep organic layers", "Explains anoxic carbon accumulation."),
            ("B", "i", "Once the water table drops, air penetrates dry peat fibres, activating aerobic microbes that oxidize millennia of stored carbon", "Explains drainage-driven oxidation."),
            ("C", "iv", "smouldering peat fires burn underground for months, releasing dense particulate plumes and surviving beneath winter snowpacks only to reignite in spring as so-called zombie fires.", "Focuses on subterranean fire hazards."),
            ("D", "ii", "Satellite flux towers confirm that raising water tables back near the surface halts carbon oxidation rapidly, though temporary spikes in methane emissions require careful hydrological monitoring.", "Covers rewetting and methane monitoring."),
        ],
        [
            ("Underground peat blazes that survive winter snowpacks are nicknamed ________.", ["zombie fires"], "C", "surviving beneath winter snowpacks only to reignite in spring as so-called zombie fires.", "Exact two-word nickname."),
            ("Rewetting quickly stops carbon oxidation but can cause short-term rises in ________.", ["methane emissions", "methane"], "D", "temporary spikes in methane emissions require careful hydrological monitoring.", "Exact two-word gas phrase."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-05",
        "Vertical Oyster Gardens on Urban Seawalls",
        "Textured concrete tiles turn sterile harbour walls into living biofilters",
        "Coastal Ecology",
        [
            ("A", "More than half the shoreline of major port cities like Sydney, Singapore, and Seattle is encased in flat concrete seawalls built to guard waterfront infrastructure against storm surge. Because sheer vertical surfaces lack crevices and tidal pools, they support far fewer algae, barnacles, and juvenile fish than natural rocky coasts."),
            ("B", "Marine ecologists have responded by bolting modular fluted tiles—engineered to mimic natural sandstone ledges and shaded micro-caves—directly onto existing seawalls. Each moulded panel retains pockets of seawater at low tide, shielding delicate intertidal organisms from scorching midday sun and hungry seabirds."),
            ("C", "Where native oysters colonize these textured habitats, water quality improves measurably alongside biodiversity. A single adult oyster filters up to one hundred and fifty litres of harbour water per day, stripping suspended silt and excess agricultural nitrogen while cementing shells together into an armour layer that buffers waves."),
            ("D", "Retrofitting seawalls nonetheless requires strict biosecurity oversight. Biologists caution that unmonitored artificial panels near busy international shipping berths can inadvertently provide footholds for invasive sea squirts carried on cargo hulls, necessitating periodic diver inspections."),
        ],
        [
            ("i", "Water-filtration and wave-buffering benefits of established shellfish"),
            ("ii", "Ecological sterility of smooth waterfront concrete walls"),
            ("iii", "Risks of invasive marine species colonizing port retrofits"),
            ("iv", "Shaded modular tiles designed to replicate rocky shoreline niches"),
            ("v", "Replacing cargo docks with recreational oyster restaurants"),
            ("vi", "Why concrete walls fail to resist coastal storm surges"),
        ],
        [
            ("A", "ii", "Because sheer vertical surfaces lack crevices and tidal pools, they support far fewer algae, barnacles, and juvenile fish", "Describes low biodiversity on flat seawalls."),
            ("B", "iv", "bolting modular fluted tiles—engineered to mimic natural sandstone ledges and shaded micro-caves", "Explains tile design."),
            ("C", "i", "A single adult oyster filters up to one hundred and fifty litres of harbour water per day, stripping suspended silt and excess agricultural nitrogen while cementing shells together into an armour layer that buffers waves.", "Highlights filtration and wave protection."),
            ("D", "iii", "can inadvertently provide footholds for invasive sea squirts carried on cargo hulls", "Flags biosecurity and invasive species risks."),
        ],
        [
            ("Fluted seawall panels trap small pools of seawater to shelter creatures from heat and ________.", ["hungry seabirds", "seabirds"], "B", "shielding delicate intertidal organisms from scorching midday sun and hungry seabirds.", "Fits NO MORE THAN TWO WORDS."),
            ("Near international shipping berths, retrofitted walls must be checked for invasive ________.", ["sea squirts"], "D", "provide footholds for invasive sea squirts carried on cargo hulls", "Exact two-word organism name."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-06",
        "Bio-Mineralizing Self-Healing Concrete",
        "Dormant limestone-producing bacteria repair microscopic cracks automatically",
        "Civil Engineering",
        [
            ("A", "Reinforced concrete bridges and tunnels inevitably develop hairline fractures under traffic vibration and freeze-thaw stress. Once micro-cracks widen past half a millimetre, rainwater and de-icing salts seep inside, corroding embedded steel rebar and forcing municipalities into multibillion-dollar structural repairs."),
            ("B", "Microbiologist Henk Jonkers developed a self-healing concrete mix containing dormant spores of alkaliphilic Bacillus bacteria alongside capsules of calcium lactate nutrient. Sealed inside dry cement, the hardy spores remain viable for decades until a crack splits the matrix and lets moisture rush in."),
            ("C", "Awakened by water and oxygen, the bacteria metabolize calcium lactate and precipitate solid calcite—essentially limestone—directly along the fracture walls. Laboratory permeability tests confirm that cracks up to 0.8 millimetres wide seal completely within three weeks, blocking further chloride ingress."),
            ("D", "Although bacterial admixtures currently double the upfront material price per cubic metre of concrete, lifecycle engineers calculate dramatic net savings on underwater piers and alpine viaducts where scaffolding access is hazardous and routine patching disrupts vital freight corridors."),
        ],
        [
            ("i", "How awakened microbes seal fissures with newly formed limestone"),
            ("ii", "Why higher initial mix costs still pay off in hard-to-reach structures"),
            ("iii", "How water and salt penetration accelerates steel bridge decay"),
            ("iv", "Embedding dormant spores and nutrients inside fresh concrete"),
            ("v", "Replacing steel rebar entirely with compressed limestone"),
            ("vi", "Health regulations banning Bacillus spores near highways"),
        ],
        [
            ("A", "iii", "rainwater and de-icing salts seep inside, corroding embedded steel rebar", "Explains how micro-cracks lead to rebar corrosion."),
            ("B", "iv", "containing dormant spores of alkaliphilic Bacillus bacteria alongside capsules of calcium lactate nutrient.", "Explains embedding spores and food."),
            ("C", "i", "metabolize calcium lactate and precipitate solid calcite—essentially limestone—directly along the fracture walls.", "Explains biological crack sealing."),
            ("D", "ii", "Although bacterial admixtures currently double the upfront material price per cubic metre of concrete, lifecycle engineers calculate dramatic net savings on underwater piers and alpine viaducts", "Weighs upfront price against lifecycle savings."),
        ],
        [
            ("Inside the concrete mix, bacterial spores are paired with capsules of ________.", ["calcium lactate"], "B", "alongside capsules of calcium lactate nutrient.", "Exact two-word nutrient name."),
            ("By sealing hairline gaps within three weeks, calcite blocks destructive ________.", ["chloride ingress"], "C", "seal completely within three weeks, blocking further chloride ingress.", "Exact two-word engineering phrase."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-07",
        "Lidar Archaeology Beneath Tropical Canopies",
        "Airborne laser pulses uncover lost cities hidden under dense rainforest",
        "Archaeology",
        [
            ("A", "For generations, dense tropical canopies in Guatemala and Cambodia forced archaeologists to survey ruins slowly with machetes and compasses, mapping barely a few square kilometres per field season. Scholars therefore assumed that classic Maya and Khmer centres consisted of compact stone temples surrounded by sparse jungle hamlets."),
            ("B", "Airborne lidar—Light Detection and Ranging—shattered that assumption by firing hundreds of thousands of near-infrared laser pulses per second from low-flying aircraft. While most pulses bounce off upper tree leaves, a small fraction slips through microscopic canopy gaps to strike the forest floor and return precise elevation data."),
            ("C", "Digital algorithms then strip away virtual vegetation, revealing subtle earthworks invisible to the naked eye: raised agricultural causeways, terraced wetlands, defensive ramparts, and tens of thousands of house mounds linking distant ceremonial plazas into sprawling low-density urban networks."),
            ("D", "Yet archaeologists stress that laser maps are hypotheses rather than finished history. Because lidar detects topography without revealing dates or artefacts, every newly spotted mound still requires painstaking ground truthing—targeted trench excavations and ceramic dating—to determine whether neighbourhoods thrived simultaneously or centuries apart."),
        ],
        [
            ("i", "How airborne laser scanning penetrates forest cover to measure terrain"),
            ("ii", "Why laser discoveries still depend on physical excavation and dating"),
            ("iii", "Previous underestimation of jungle settlements due to manual surveying"),
            ("iv", "Vast hidden agricultural and residential infrastructure exposed digitally"),
            ("v", "Satellite radar proving Maya cities abandoned causeway farming"),
            ("vi", "How laser pulses damage fragile limestone carvings"),
        ],
        [
            ("A", "iii", "Scholars therefore assumed that classic Maya and Khmer centres consisted of compact stone temples surrounded by sparse jungle hamlets.", "Explains past surveying constraints and assumptions."),
            ("B", "i", "a small fraction slips through microscopic canopy gaps to strike the forest floor and return precise elevation data.", "Explains lidar mechanics."),
            ("C", "iv", "revealing subtle earthworks invisible to the naked eye: raised agricultural causeways, terraced wetlands, defensive ramparts", "Summarizes revealed urban networks."),
            ("D", "ii", "every newly spotted mound still requires painstaking ground truthing—targeted trench excavations and ceramic dating", "Stresses necessity of fieldwork verification."),
        ],
        [
            ("Lidar aircraft emit hundreds of thousands of ________ pulses every second.", ["near-infrared laser", "laser"], "B", "firing hundreds of thousands of near-infrared laser pulses per second", "Hyphenated 'near-infrared' counts as 1 word."),
            ("Verifying digital terrain maps through physical trench work is termed ________.", ["ground truthing"], "D", "requires painstaking ground truthing—targeted trench excavations", "Exact two-word archaeological term."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-08",
        "Agrivoltaics: Farming Under Solar Arrays",
        "Elevated solar panels simultaneously cut crop water loss and boost panel efficiency",
        "Renewable Energy & Agronomy",
        [
            ("A", "Expanding utility-scale solar farms often sparks fierce land-use conflicts when photovoltaic arrays compete with fertile farmland. Agrivoltaics resolves that zero-sum rivalry by elevating translucent or spaced solar panels three to four metres above active fields so tractors and livestock operate seamlessly underneath."),
            ("B", "Field experiments in Arizona and southern France uncovered a mutually beneficial microclimate beneath the arrays. Partial afternoon shade lowers leaf heat stress in lettuce, tomatoes, and peppers, slashing irrigation evaporation by up to thirty percent during summer heatwaves."),
            ("C", "Remarkably, the solar hardware benefits as well. Silicon photovoltaic cells lose conversion efficiency whenever panel temperatures soar past twenty-five degrees Celsius; moisture transpired continuously by thriving crops below cools the underside of the arrays by nearly nine degrees, lifting electricity output during peak midday sun."),
            ("D", "Adoption still faces practical hurdles: taller steel mounting racks raise installation costs by roughly fifteen percent, and sun-loving cereal staples such as wheat or maize show yield drops under dense shade. Agronomists are now mapping crop-specific spacing formulas so farmers pair the right shade-tolerant species with local utility grids."),
        ],
        [
            ("i", "How evaporating crop moisture cools panels and lifts power output"),
            ("ii", "Higher mounting costs and crop-type limitations to overcome"),
            ("iii", "Elevating solar infrastructure to end competition with agriculture"),
            ("iv", "Water savings and heat relief for vegetables grown under shade"),
            ("v", "Why livestock refuse to graze beneath elevated solar racks"),
            ("vi", "Eliminating silicon cells in favour of transparent glass roofs"),
        ],
        [
            ("A", "iii", "resolves that zero-sum rivalry by elevating translucent or spaced solar panels three to four metres above active fields", "Introduces agrivoltaics as dual land use."),
            ("B", "iv", "Partial afternoon shade lowers leaf heat stress in lettuce, tomatoes, and peppers, slashing irrigation evaporation by up to thirty percent during summer heatwaves.", "Details agronomic benefits."),
            ("C", "i", "moisture transpired continuously by thriving crops below cools the underside of the arrays by nearly nine degrees, lifting electricity output during peak midday sun.", "Explains reciprocal cooling benefit to solar panels."),
            ("D", "ii", "taller steel mounting racks raise installation costs by roughly fifteen percent, and sun-loving cereal staples such as wheat or maize show yield drops under dense shade.", "Outlines financial and crop constraints."),
        ],
        [
            ("Silicon solar panels lose efficiency when operating temperatures rise above ________.", ["twenty-five degrees"], "C", "whenever panel temperatures soar past twenty-five degrees Celsius", "Hyphenated 'twenty-five' counts as 1 word."),
            ("Grain staples like wheat and maize suffer ________ beneath heavy panel shade.", ["yield drops"], "D", "wheat or maize show yield drops under dense shade.", "Exact two-word noun phrase."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-09",
        "The Mechanics of Migratory Bird Magnetoreception",
        "Quantum compass reactions inside avian retinas help songbirds sense Earth's magnetic field",
        "Sensory Biology",
        [
            ("A", "Every autumn, juvenile European robins that have never flown south before depart Scandinavia alone at night and arrive unerringly in Mediterranean wintering grounds. While stars and sunset polarization help calibrate direction, controlled cage trials proved that songbirds still orient accurately even under completely overcast skies by sensing Earth's geomagnetic field."),
            ("B", "For decades, biologists puzzled over how a magnetic field weaker than a refrigerator magnet could trigger nerve signals inside living tissue. A leading hypothesis focuses on cryptochrome—a light-sensitive protein embedded in the bird's retina—where blue photons generate pairs of entangled electrons whose chemical spin responds delicately to magnetic inclination."),
            ("C", "Crucially, this retinal compass does not distinguish north from south like a hiking needle; instead, it measures the dip angle between magnetic field lines and Earth's surface, telling birds whether they are flying poleward or equatorward. Experiments exposing robins to weak urban radio-frequency noise temporarily scrambled this quantum sensor, lending dramatic support to the cryptochrome mechanism."),
            ("D", "Neurobiologists note that birds likely rely on a redundant dual-sensor toolkit. Alongside the light-dependent retinal compass, microscopic magnetite crystals near the upper beak appear to operate as an intensity map that tells experienced migrants roughly how far along their migratory corridor they have travelled."),
        ],
        [
            ("i", "A light-activated retinal protein linked to quantum electron spins"),
            ("ii", "A second magnetic sensor acting as a positional distance map"),
            ("iii", "Evidence that songbirds navigate magnetically without clear skies"),
            ("iv", "How inclination angles work and why radio noise disrupts them"),
            ("v", "Why juvenile robins must follow adult flocks on their first flight"),
            ("vi", "Proof that overcast nights halt autumn bird migration"),
        ],
        [
            ("A", "iii", "songbirds still orient accurately even under completely overcast skies by sensing Earth's geomagnetic field.", "Establishes innate geomagnetic navigation."),
            ("B", "i", "focuses on cryptochrome—a light-sensitive protein embedded in the bird's retina—where blue photons generate pairs of entangled electrons", "Explains cryptochrome quantum compass."),
            ("C", "iv", "Experiments exposing robins to weak urban radio-frequency noise temporarily scrambled this quantum sensor, lending dramatic support to the cryptochrome mechanism.", "Explains inclination compass and RF disruption."),
            ("D", "ii", "microscopic magnetite crystals near the upper beak appear to operate as an intensity map", "Introduces the secondary magnetite map sensor."),
        ],
        [
            ("Blue light triggers magnetically sensitive electron pairs inside a retinal protein called ________.", ["cryptochrome"], "B", "focuses on cryptochrome—a light-sensitive protein embedded in the bird's retina", "Single scientific noun."),
            ("Tiny ________ near the beak may provide migrants with an intensity-based position map.", ["magnetite crystals"], "D", "microscopic magnetite crystals near the upper beak appear to operate as an intensity map", "Exact two-word noun phrase."),
        ],
    ),
    _make_p2_drill(
        "drill-p2-10",
        "Sponge Cities and Urban River Daylighting",
        "Uncovering buried concrete-piped streams reduces flash floods and revives urban ecology",
        "Hydrology & Urban Planning",
        [
            ("A", "Throughout the nineteenth and twentieth centuries, rapidly industrializing cities buried thousands of urban creeks inside underground brick culverts to clear land for factories and boulevards. Yet impervious concrete streets funnel cloudburst rainfall into those narrow pipes far faster than soil absorbs water, triggering destructive basement flooding whenever storms intensify."),
            ("B", "A growing movement known as river daylighting reverses that legacy by excavating buried waterways and restoring open vegetated riverbanks. In Seoul, dismantling a decaying elevated expressway to uncover the Cheonggyecheon stream lowered surrounding summer air temperatures by more than three degrees while turning a congested corridor into a bustling linear park."),
            ("C", "Hydrologists point out that daylighted channels work best when integrated into a wider 'sponge city' watershed—bioswales, sunken rain gardens, and permeable parking lots that slow stormwater upstream before it ever reaches the river. Without upstream retention, an uncovered urban stream can still surge violently during extreme monsoon events."),
            ("D", "Critics initially balked at the upfront civil-engineering price of relocating underground utility mains and replacing aging culverts. Municipal audits in Zurich and Auckland, however, revealed that open naturalistic channels cost significantly less to maintain over fifty years than repeatedly repairing corroded concrete storm sewers."),
        ],
        [
            ("i", "Why uncovered channels must be paired with upstream water absorption"),
            ("ii", "Long-term maintenance savings offsetting high excavation outlays"),
            ("iii", "How burying city streams worsened modern flash-flood vulnerability"),
            ("iv", "Cooling and public-space gains from unearthing an urban waterway"),
            ("v", "Why Zurich returned to underground brick storm sewers"),
            ("vi", "Banning elevated highways across all Asian capitals"),
        ],
        [
            ("A", "iii", "Yet impervious concrete streets funnel cloudburst rainfall into those narrow pipes far faster than soil absorbs water, triggering destructive basement flooding whenever storms intensify.", "Explains historical burial and flooding problem."),
            ("B", "iv", "In Seoul, dismantling a decaying elevated expressway to uncover the Cheonggyecheon stream lowered surrounding summer air temperatures by more than three degrees while turning a congested corridor into a bustling linear park.", "Showcases daylighting benefits in Seoul."),
            ("C", "i", "Without upstream retention, an uncovered urban stream can still surge violently during extreme monsoon events.", "Stresses watershed-wide retention."),
            ("D", "ii", "open naturalistic channels cost significantly less to maintain over fifty years than repeatedly repairing corroded concrete storm sewers.", "Compares upfront cost vs 50-year savings."),
        ],
        [
            ("Restoring buried underground creeks to open vegetated channels is called ________.", ["river daylighting", "daylighting"], "B", "A growing movement known as river daylighting reverses that legacy", "Exact two-word term."),
            ("Upstream bioswales and ________ slow rainwater before it reaches an open channel.", ["rain gardens"], "C", "bioswales, sunken rain gardens, and permeable parking lots that slow stormwater upstream", "Fits NO MORE THAN TWO WORDS."),
        ],
    ),
]
