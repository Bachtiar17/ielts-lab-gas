"""Original Academic Reading Drill Bank — Slot 1 (10 Passage-1 style drills).

Every passage is 100% original academic prose (zero copyrighted source material)
and every evidence_span.quote is verified verbatim against its target paragraph.
"""

from __future__ import annotations

from typing import Any


def _make_p1_drill(
    slug: str,
    title: str,
    subtitle: str,
    topic: str,
    paragraphs: list[tuple[str, str]],
    tfng_items: list[tuple[str, str, str, str, str]],
    comp_items: list[tuple[str, list[str], str, str, str]],
) -> dict[str, Any]:
    """Build a standardized Passage-1 style 6-question drill (3 T/F/NG + 3 ONE WORD ONLY completion)."""
    questions: list[dict[str, Any]] = []
    for idx, (prompt, ans, pid, quote, note) in enumerate(tfng_items, start=1):
        questions.append(
            {
                "id": f"{slug}-q{idx:02d}",
                "passage_index": 1,
                "question_number": idx,
                "question_type": "tfng",
                "target_band": 6.0 if idx <= 2 else 6.5,
                "prompt_payload": {"group_id": f"{slug}-g1", "prompt": prompt},
                "answer_key": {"accepted": [ans]},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    wl = {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}
    for offset, (prompt, accepted, pid, quote, note) in enumerate(comp_items, start=4):
        questions.append(
            {
                "id": f"{slug}-q{offset:02d}",
                "passage_index": 1,
                "question_number": offset,
                "question_type": "note_table_flowchart_completion",
                "target_band": 6.5,
                "prompt_payload": {"group_id": f"{slug}-g2", "prompt": prompt, "word_limit": wl},
                "answer_key": {"accepted": accepted, "word_limit": wl},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    return {
        "id": slug,
        "title": title,
        "subtitle": subtitle,
        "difficulty_label": "Passage 1 · Band 6.0–7.0",
        "duration_minutes": 15,
        "drill_slot": 1,
        "passages": [
            {
                "index": 1,
                "title": title,
                "subtitle": subtitle,
                "topic": topic,
                "recommended_minutes": 15,
                "paragraphs": [{"id": pid, "text": txt} for pid, txt in paragraphs],
                "question_groups": [
                    {
                        "id": f"{slug}-g1",
                        "title": "Questions 1–3",
                        "question_type": "tfng",
                        "instructions": "Choose TRUE if the statement agrees with the passage, FALSE if it contradicts it, or NOT GIVEN if there is no information.",
                        "question_numbers": [1, 2, 3],
                    },
                    {
                        "id": f"{slug}-g2",
                        "title": "Questions 4–6",
                        "question_type": "note_table_flowchart_completion",
                        "instructions": "Complete the notes below. Choose ONE WORD ONLY from the passage for each answer.",
                        "word_limit": wl,
                        "question_numbers": [4, 5, 6],
                    },
                ],
            }
        ],
        "questions": questions,
    }


P1_DRILLS: list[dict[str, Any]] = [
    _make_p1_drill(
        "drill-p1-01",
        "Ice Houses of the Pre-Refrigeration Era",
        "How brick-lined underground vaults stored winter ice through blistering summers",
        "History of Technology",
        [
            ("A", "Long before electric compressors cooled commercial warehouses, wealthy estates and port towns across Europe and Persia relied on subterranean ice houses to preserve perishable foods through summer heat. Builders typically dug deep circular pits into north-facing hillsides where overhanging trees blocked direct sunlight. Inside, thick masonry walls lined with straw or sawdust created an insulating barrier that slowed melting to a trickle."),
            ("B", "Harvesting ice was a synchronized winter industry. During January freezes, crews sawed clean freshwater ponds into uniform rectangular blocks, hauling them by horse-drawn sled to the vault before midday temperatures rose. Workers packed each layer tightly and sprinkled rock salt only on drainage floors—never directly onto stored blocks, since salt accelerates thawing. Meltwater drained through a grated sump at the base so the remaining ice stayed dry and dense."),
            ("C", "By the 1840s, American entrepreneur Frederic Tudor had turned natural ice into an international commodity, shipping New England lake ice packed in pine sawdust all the way to Calcutta and Havana. Although skeptics ridiculed the venture as folly, ships routinely arrived with more than two-thirds of their frozen cargo intact, proving that passive thermal insulation could rival early mechanical chillers."),
        ],
        [
            ("Ice houses were commonly constructed on south-facing slopes to maximize winter airflow.", "FALSE", "A", "Builders typically dug deep circular pits into north-facing hillsides where overhanging trees blocked direct sunlight.", "Direction reversal trap: north-facing hillsides were used to avoid direct sunlight, not south-facing slopes."),
            ("Workers avoided sprinkling salt directly onto stored ice blocks.", "TRUE", "B", "sprinkled rock salt only on drainage floors—never directly onto stored blocks, since salt accelerates thawing.", "Directly confirmed in Paragraph B."),
            ("Frederic Tudor personally designed the insulated cargo hulls used on ice ships.", "NOT GIVEN", "C", "shipping New England lake ice packed in pine sawdust all the way to Calcutta and Havana.", "Tudor's shipping business is described, but whether he personally designed ship hulls is never mentioned."),
        ],
        [
            ("Masonry walls were insulated internally using straw or ________.", ["sawdust"], "A", "thick masonry walls lined with straw or sawdust created an insulating barrier", "Exact single word paired with straw."),
            ("A grated ________ at the bottom of the pit carried meltwater away.", ["sump"], "B", "Meltwater drained through a grated sump at the base", "Exact noun after 'grated'."),
            ("Over two-thirds of Tudor's exported ice reached tropical ports still ________.", ["intact"], "C", "ships routinely arrived with more than two-thirds of their frozen cargo intact", "Single adjective directly from Paragraph C."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-02",
        "The Rise of Botanical Glasshouses",
        "Cast-iron framing and sheet glass transformed Victorian plant science",
        "Architectural History",
        [
            ("A", "Early seventeenth-century orangeries were bulky stone pavilions with tall south-facing windows and coal stoves that kept citrus trees barely alive during frosts. Because opaque roofs blocked overhead illumination, tropical ferns and orchids frequently withered even when indoor temperatures remained warm. Everything changed in the 1830s when British glassmakers perfected cylinder-blown sheet glass, lowering pane costs and letting engineers glaze entire curved roofs."),
            ("B", "Horticulturist Joseph Paxton pioneered ridge-and-furrow glazing at Chatsworth, angling glass panes so morning and evening winter sunlight struck at near-perpendicular angles while heavy hail deflected harmlessly. Hollow cast-iron columns served a dual purpose: they supported the airy roof lattice while channelling rainwater straight into underground cisterns used for misting delicate foliage."),
            ("C", "At Kew Gardens, the Palm House demonstrated how prefabricated wrought-iron ribs could span twenty metres without internal pillars, creating a humid microclimate that allowed botanists to study cinchona and rubber seedlings far from the Amazon. These structures were never mere aristocratic ornaments; they served as living laboratories for global agronomy."),
        ],
        [
            ("Early stone orangeries struggled to keep tropical plants healthy primarily because their roofs blocked overhead light.", "TRUE", "A", "Because opaque roofs blocked overhead illumination, tropical ferns and orchids frequently withered even when indoor temperatures remained warm.", "Directly supported by Paragraph A."),
            ("Joseph Paxton's cast-iron columns were strictly decorative and carried no rainwater.", "FALSE", "B", "Hollow cast-iron columns served a dual purpose: they supported the airy roof lattice while channelling rainwater straight into underground cisterns", "Contradicts the dual structural and drainage function described in Paragraph B."),
            ("The Palm House at Kew Gardens cost twice as much to heat as the Chatsworth conservatory.", "NOT GIVEN", "C", "the Palm House demonstrated how prefabricated wrought-iron ribs could span twenty metres without internal pillars", "No heating cost comparison appears in the passage."),
        ],
        [
            ("Cylinder-blown sheet glass enabled engineers to cover curved ________ entirely in glass.", ["roofs"], "A", "lowering pane costs and letting engineers glaze entire curved roofs.", "Plural noun matching 'curved'."),
            ("Paxton's hollow columns directed rainwater into subterranean ________.", ["cisterns"], "B", "channelling rainwater straight into underground cisterns used for misting delicate foliage.", "'subterranean' paraphrases 'underground'."),
            ("Botanists at Kew cultivated cinchona and ________ seedlings inside the Palm House.", ["rubber"], "C", "allowed botanists to study cinchona and rubber seedlings far from the Amazon.", "Exact single word before 'seedlings'."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-03",
        "Polynesian Wayfinding Without Instruments",
        "Star compasses, ocean swells, and seabirds guided double-hulled canoes across the Pacific",
        "Maritime Anthropology",
        [
            ("A", "Centuries before magnetic compasses reached European decks, Polynesian navigators routinely crossed thousands of kilometres of open Pacific Ocean in double-hulled voyaging canoes. Rather than relying on paper charts or sextants, master wayfinders memorized a mental 'star compass', noting exact horizon points where bright constellations rose and set. Because stars trace predictable arcs near the equator, a single rising beacon could anchor a canoe's heading for hours."),
            ("B", "When cloud cover obscured the night sky, navigators shifted attention to ocean swells—long-wavelength waves generated by distant trade winds rather than local squalls. By lying quietly against the wooden hull, an experienced wayfinder could feel subtle interference patterns created when swells refracted around an unseen island up to fifty kilometres away. Changes in water temperature and phosphorescent plankton trails offered supplementary confirmation."),
            ("C", "Daylight landfinding drew upon avian ecology. Terns and noddies fish out at sea during morning hours but return to roost on dry land before dusk, acting as living pointers toward atolls too low to break the horizon. In 1976, the replica canoe Hokulea sailed from Hawaii to Tahiti without a single modern instrument, silencing claims that Pacific settlement had resulted from accidental drift."),
        ],
        [
            ("Polynesian wayfinders depended on magnetic compasses traded from East Asia.", "FALSE", "A", "Rather than relying on paper charts or sextants, master wayfinders memorized a mental 'star compass'", "Directly contradicts instrument-based navigation."),
            ("Skilled navigators could detect distant islands through wave patterns felt through the canoe's hull.", "TRUE", "B", "By lying quietly against the wooden hull, an experienced wayfinder could feel subtle interference patterns created when swells refracted around an unseen island", "Directly confirmed in Paragraph B."),
            ("The 1976 voyage of the Hokulea took forty-two days to complete.", "NOT GIVEN", "C", "In 1976, the replica canoe Hokulea sailed from Hawaii to Tahiti without a single modern instrument", "The year and route are stated, not the duration in days."),
        ],
        [
            ("Long-wavelength ocean ________ were produced by distant trade winds.", ["swells"], "B", "ocean swells—long-wavelength waves generated by distant trade winds", "Exact plural noun defined in Paragraph B."),
            ("Seabirds such as terns and ________ flew back toward land each evening.", ["noddies"], "C", "Terns and noddies fish out at sea during morning hours but return to roost on dry land before dusk", "Paired bird species name."),
            ("The 1976 Hokulea crossing disproved theories that Pacific islands were settled by accidental ________.", ["drift"], "C", "silencing claims that Pacific settlement had resulted from accidental drift.", "Exact final noun of Paragraph C."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-04",
        "The Forgotten Craft of Lighthouse Lenses",
        "How Augustin-Jean Fresnel replaced smoky mirrors with concentric glass prisms",
        "Optics & Engineering",
        [
            ("A", "Before 1820, coastal lighthouses wasted nearly ninety percent of their lamp output. Parabolic metal reflectors tarnished rapidly in salty air and scattered feeble yellow rays that vanished in Atlantic fog. French physicist Augustin-Jean Fresnel solved this crisis by slicing a thick convex lens into concentric stepped rings mounted in a brass beehive frame, dramatically cutting weight while concentrating light into a razor-sharp horizontal beam."),
            ("B", "Installed first at the Cordouan Lighthouse in 1823, Fresnel's dioptric lens was visible from over thirty kilometres away—more than triple the range of earlier reflectors. Because a giant first-order assembly weighed over two tonnes, engineers floated the entire rotating turret in a circular trough of liquid mercury, eliminating friction so cleanly that a clockwork weight could spin the lens with a single finger's push."),
            ("C", "Although modern LED beacons have replaced kerosene mantles and mercury baths for safety reasons, dozens of nineteenth-century Fresnel optics remain active along rocky coastlines today. Maritime historians regard the stepped prism design as one of the rare inventions that saved countless lives immediately upon deployment."),
        ],
        [
            ("Early metal lighthouse reflectors lost most of their light output and corroded quickly near the sea.", "TRUE", "A", "Before 1820, coastal lighthouses wasted nearly ninety percent of their lamp output. Parabolic metal reflectors tarnished rapidly in salty air", "Confirmed by 'wasted nearly ninety percent' and 'tarnished rapidly'."),
            ("First-order Fresnel lenses were rotated using high-voltage electric motors in 1823.", "FALSE", "B", "eliminating friction so cleanly that a clockwork weight could spin the lens with a single finger's push.", "A clockwork weight powered rotation, not electric motors."),
            ("Fresnel received a royal pension from the British Admiralty for his invention.", "NOT GIVEN", "C", "Maritime historians regard the stepped prism design as one of the rare inventions that saved countless lives", "No British royal pension is mentioned."),
        ],
        [
            ("Fresnel arranged stepped concentric glass rings inside a ________ frame.", ["brass"], "A", "slicing a thick convex lens into concentric stepped rings mounted in a brass beehive frame", "Material adjective before 'frame'."),
            ("Engineers reduced friction by floating heavy rotating lenses in a trough of liquid ________.", ["mercury"], "B", "engineers floated the entire rotating turret in a circular trough of liquid mercury", "Exact substance name."),
            ("Modern beacons have largely replaced kerosene mantles with ________ units.", ["LED"], "C", "Although modern LED beacons have replaced kerosene mantles", "Single-word acronym matching 'units'."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-05",
        "Desert Fog Harvesters of the Atacama",
        "Polypropylene mesh curtains turn coastal mist into drinking water",
        "Environmental Engineering",
        [
            ("A", "Along the arid Pacific coast of northern Chile, certain stretches of the Atacama Desert receive less than two millimetres of rainfall per decade. Yet cold ocean currents offshore generate dense banks of marine stratocumulus fog—locally called camanchaca—that roll inland across coastal ridges almost every dawn. Inspired by Namib desert beetles that condense mist on textured wing cases, engineers erected vertical fine-mesh curtains perpendicular to prevailing winds."),
            ("B", "As microscopic fog droplets drift through the double-layer polypropylene netting, they coalesce on slender filaments until gravity pulls them downward into a PVC gutter. A single forty-square-metre collector can yield between two hundred and four hundred litres of clean freshwater on a foggy morning without consuming a single watt of electricity. Community installations near Chungungo once piped harvested fog water directly into household taps and terraced olive groves."),
            ("C", "Long-term field evaluations reveal that windstorms and ultraviolet degradation remain the chief maintenance challenges, requiring villagers to tension cables and replace weathered netting every five to seven years. Even so, hydrologists view passive fog catching as a vital low-carbon supplement for isolated mountain settlements far from municipal aqueducts."),
        ],
        [
            ("Coastal Atacama fog is formed by warm tropical ocean currents.", "FALSE", "A", "cold ocean currents offshore generate dense banks of marine stratocumulus fog", "Contradicts 'cold ocean currents'."),
            ("Fog-harvesting mesh collectors require no electrical power to produce drinking water.", "TRUE", "B", "can yield between two hundred and four hundred litres of clean freshwater on a foggy morning without consuming a single watt of electricity.", "Directly confirmed."),
            ("Olive oil produced in Chungungo sells at a premium price in Santiago supermarkets.", "NOT GIVEN", "B", "piped harvested fog water directly into household taps and terraced olive groves.", "Olive groves are mentioned, not retail pricing in Santiago."),
        ],
        [
            ("Engineers drew biomimetic inspiration from the textured wing cases of desert ________.", ["beetles"], "A", "Inspired by Namib desert beetles that condense mist on textured wing cases", "Exact plural noun."),
            ("Coalesced water droplets flow down the netting into a PVC ________.", ["gutter"], "B", "until gravity pulls them downward into a PVC gutter.", "Exact single word after PVC."),
            ("Strong winds and ________ degradation force crews to replace netting periodically.", ["ultraviolet"], "C", "windstorms and ultraviolet degradation remain the chief maintenance challenges", "Exact single word before 'degradation'."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-06",
        "The Underground Postal Railways of London",
        "Driverless electric trains ferried four million letters a day beneath congested streets",
        "Urban Transport History",
        [
            ("A", "By 1911, horse-drawn mail vans crawling through London's fog-bound thoroughfares routinely delayed deliveries between sorting depots and mainline railway stations. To bypass surface gridlock altogether, the General Post Office bored a ten-kilometre narrow-gauge tunnel twenty metres beneath Oxford Street and Holborn. Opened in December 1927, the Post Office Railway—later nicknamed Mail Rail—operated entirely without onboard drivers."),
            ("B", "Instead of carrying human operators, miniature electric locomotives drew power from segmented track sections controlled remotely from underground switch cabins. Station staff slid wheeled mail containers onto flatcars, flipped a lever, and watched trains accelerate smoothly up to fifty-five kilometres per hour through curved cast-iron tubes. At its peak in the 1960s, the subterranean loop transported roughly four million letters daily across eight sorting offices."),
            ("C", "Decades later, as automated sorting hubs relocated outside central London to be closer to motorways, operating costs per sack climbed steeply until services ceased in May 2003. Rather than sealing the tunnels permanently, engineers preserved a short stretch beneath Mount Pleasant, reopening it in 2017 as a heritage ride that reveals the hidden logistics of twentieth-century communication."),
        ],
        [
            ("Mail Rail trains required a human driver seated in the front carriage.", "FALSE", "A", "the Post Office Railway—later nicknamed Mail Rail—operated entirely without onboard drivers.", "Explicitly driverless."),
            ("The underground postal network moved approximately four million letters each day at its busiest period.", "TRUE", "B", "At its peak in the 1960s, the subterranean loop transported roughly four million letters daily", "Directly confirmed."),
            ("Mail Rail tunnels were briefly used as public air-raid shelters during the 1940s.", "NOT GIVEN", "C", "operating costs per sack climbed steeply until services ceased in May 2003.", "Wartime shelter usage is never mentioned."),
        ],
        [
            ("Mail Rail was excavated twenty metres underneath ________ Street and Holborn.", ["Oxford"], "A", "bored a ten-kilometre narrow-gauge tunnel twenty metres beneath Oxford Street and Holborn.", "Proper noun before 'Street'."),
            ("Train power was regulated remotely from underground ________ cabins.", ["switch"], "B", "controlled remotely from underground switch cabins.", "Exact modifier before 'cabins'."),
            ("The railway closed in 2003 after modern sorting centres moved closer to ________.", ["motorways"], "C", "automated sorting hubs relocated outside central London to be closer to motorways", "Exact plural noun."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-07",
        "Silk from Sea Shells: The Story of Byssus",
        "Mediterranean artisans spun golden cloth from filaments secreted by giant pen shells",
        "Textile History",
        [
            ("A", "Most historians associate ancient luxury silk with mulberry-fed silkworms from China, yet Mediterranean coastal workshops once produced an even rarer golden fibre harvested from the seabed. Known as sea silk or byssus, the thread comes from Pinna nobilis, a giant fan-shaped mollusc that anchors itself to sandy seagrass meadows using tufts of fine protein filaments."),
            ("B", "Divers carefully detached the anchoring tufts, washed them in freshwater to strip away sea salt, and soaked the fibres in lemon juice to bring out an iridescent bronze-gold sheen that never faded. Because each mollusc yielded barely a gram of usable strand after combing, weaving a single pair of ceremonial gloves required filaments from hundreds of shells. Unlike silkworm silk, sea silk could not be dyed effectively; its natural metallic hue was prized precisely because it resisted chemical pigments."),
            ("C", "Today, Pinna nobilis is critically endangered across the Mediterranean due to coastal dredging and a devastating parasitic pathogen detected in 2016. Harvesting wild shells is strictly prohibited under European conservation law, leaving only a handful of elderly Sardinian craftswomen preserving historic sea-silk spinning techniques for museum archives."),
        ],
        [
            ("Sea silk fibres were harvested from a large marine mollusc living in seagrass meadows.", "TRUE", "A", "comes from Pinna nobilis, a giant fan-shaped mollusc that anchors itself to sandy seagrass meadows using tufts of fine protein filaments.", "Directly confirmed."),
            ("Mediterranean weavers routinely dyed sea silk bright crimson using crushed beetles.", "FALSE", "B", "Unlike silkworm silk, sea silk could not be dyed effectively; its natural metallic hue was prized", "Explicitly contradicts dyeing."),
            ("Roman emperors outlawed private citizens from wearing sea-silk cloaks.", "NOT GIVEN", "B", "weaving a single pair of ceremonial gloves required filaments from hundreds of shells.", "Roman sumptuary laws are not mentioned."),
        ],
        [
            ("Artisans soaked the washed filaments in ________ juice to reveal a golden lustre.", ["lemon"], "B", "soaked the fibres in lemon juice to bring out an iridescent bronze-gold sheen", "Exact single word before 'juice'."),
            ("After combing, one mollusc produced less than a ________ of usable thread.", ["gram"], "B", "each mollusc yielded barely a gram of usable strand after combing", "Unit noun matching 'a ________'."),
            ("A parasitic ________ identified in 2016 severely threatened remaining Pinna nobilis populations.", ["pathogen"], "C", "due to coastal dredging and a devastating parasitic pathogen detected in 2016.", "Exact noun after 'parasitic'."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-08",
        "Acoustic Mirrors of the English Coast",
        "Before radar existed, giant concrete dishes listened for approaching aircraft",
        "Military & Acoustic History",
        [
            ("A", "Long before pulsed radio waves tracked planes across the sky, British physicist William Sansome Tucker designed monumental concave concrete bowls along the Kent coastline to hear enemy bombers over the English Channel. Built between 1928 and 1935 at Denge, these acoustic mirrors—nicknamed 'listening ears'—ranged from six-metre circular dishes to a curving sixty-metre concrete wall."),
            ("B", "Sound waves from distant propellers struck the smooth parabolic surface and converged onto a focal microphone suspended in front of the dish. Trained listeners wearing headphones could detect twin-engine aircraft up to forty kilometres offshore, granting coastal defenders roughly fifteen minutes of advance warning. Yet the system suffered from fatal limitations: roaring surf, passing cargo ships, and faster monoplanes rapidly overwhelmed operators."),
            ("C", "When Robert Watson-Watt demonstrated practical radio detection in 1935, funding shifted overnight from acoustics to radar towers. The concrete mirrors were left standing on shingle marshes, where they now serve as eerie architectural landmarks and unlikely nesting ledges for coastal kestrels."),
        ],
        [
            ("The largest acoustic mirror constructed at Denge was a curved concrete wall sixty metres long.", "TRUE", "A", "ranged from six-metre circular dishes to a curving sixty-metre concrete wall.", "Confirmed in Paragraph A."),
            ("Acoustic mirrors remained unaffected by ocean waves and nearby ships.", "FALSE", "B", "roaring surf, passing cargo ships, and faster monoplanes rapidly overwhelmed operators.", "Directly contradicted by Paragraph B."),
            ("William Sansome Tucker later helped build the first radar stations in Scotland.", "NOT GIVEN", "C", "When Robert Watson-Watt demonstrated practical radio detection in 1935, funding shifted overnight", "Tucker's post-1935 career is never discussed."),
        ],
        [
            ("Incoming engine noise focused onto a suspended ________ placed ahead of the dish.", ["microphone"], "B", "converged onto a focal microphone suspended in front of the dish.", "Exact device noun."),
            ("Acoustic detection offered coastal defences around fifteen minutes of early ________.", ["warning"], "B", "granting coastal defenders roughly fifteen minutes of advance warning.", "'early' paraphrases 'advance'."),
            ("Today, the abandoned concrete walls provide nesting sites for coastal ________.", ["kestrels"], "C", "unlikely nesting ledges for coastal kestrels.", "Exact plural bird name."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-09",
        "The Ancient Seed Vaults of Qanat Villages",
        "Subterranean water channels sustained drought-hardy landraces across Iranian plateaus",
        "Agricultural History",
        [
            ("A", "In arid highland valleys of central Iran, farmers have cultivated wheat, pomegranates, and pistachios for over two millennia using qanats—gently sloping underground tunnels that tap mountain aquifers and deliver groundwater to desert oases strictly by gravity. Because the water flows beneath baked clay rather than across open ditches, evaporation losses remain minimal even in forty-degree summer winds."),
            ("B", "Equally vital to village survival were communal earthen granaries where elders curated dozens of locally adapted seed strains known as landraces. Each autumn, families set aside the plumpest barley and chickpea grains from plots that had survived unseasonable frost or salty irrigation water. Over centuries, this decentralized selection created crops with deep root systems capable of thriving on sparse qanat allocations."),
            ("C", "Modern deep-well diesel pumps lowered regional water tables rapidly during the late twentieth century, drying up hundreds of historic qanats and pushing farmers toward uniform commercial hybrids. Agronomists are now partnering with village cooperatives to catalogue surviving landraces before irreplaceable drought-tolerance genes vanish."),
        ],
        [
            ("Qanat tunnels rely on mechanical pumps to lift groundwater toward desert farms.", "FALSE", "A", "deliver groundwater to desert oases strictly by gravity.", "Gravity-fed, not mechanically pumped."),
            ("Underground qanat channels lose very little water to summer evaporation.", "TRUE", "A", "Because the water flows beneath baked clay rather than across open ditches, evaporation losses remain minimal", "Directly confirmed."),
            ("Iranian village granaries were legally required to donate ten percent of stored seeds to regional governors.", "NOT GIVEN", "B", "families set aside the plumpest barley and chickpea grains from plots that had survived unseasonable frost", "No taxation or governor donation is mentioned."),
        ],
        [
            ("Locally adapted crop varieties maintained in village granaries are called ________.", ["landraces"], "B", "curated dozens of locally adapted seed strains known as landraces.", "Exact plural term."),
            ("Selective saving produced crops with deep ________ systems suited to scarce water.", ["root"], "B", "created crops with deep root systems capable of thriving on sparse qanat allocations.", "Exact single word before 'systems'."),
            ("Widespread adoption of diesel ________ caused regional water tables to fall.", ["pumps"], "C", "Modern deep-well diesel pumps lowered regional water tables rapidly", "Exact plural noun after 'diesel'."),
        ],
    ),
    _make_p1_drill(
        "drill-p1-10",
        "Paper Bridges of Edo-Period Mapmakers",
        "How surveyor Ino Tadataka walked forty thousand kilometres to map Japan",
        "History of Cartography",
        [
            ("A", "At age fifty, retired sake brewer Ino Tadataka moved to Edo to study astronomy and mathematics, embarking on an extraordinary second career. Between 1800 and 1816, Tadataka and a small surveying team marched nearly forty thousand kilometres along Japan's rugged coastline, measuring distances with iron chains and pacing strides calibrated against nightly star observations."),
            ("B", "Every evening at local inns, the team transferred raw bearings onto handmade mulberry paper using fine bamboo dividers. To guard against cumulative drift over hundreds of kilometres, Tadataka cross-checked coastal traverses with astronomical latitude measurements obtained through a portable quadrant. The resulting Dai-Nihon Enkai Yochi Zenzu comprised over two hundred large hand-painted sheets accurate enough to astonish British naval hydrographers decades later."),
            ("C", "Tadataka died three years before the final atlas was presented to the shogunate in 1821, leaving his apprentices to complete the delicate brushwork. Remarkably, satellite overlays conducted in the twenty-first century confirm that his coastal contours deviate by less than one-thousandth of a degree along most major bays."),
        ],
        [
            ("Ino Tadataka began his coastal surveying work after retiring from brewing sake.", "TRUE", "A", "At age fifty, retired sake brewer Ino Tadataka moved to Edo to study astronomy and mathematics, embarking on an extraordinary second career.", "Confirmed in Paragraph A."),
            ("Tadataka completed the final presentation of his atlas to the shogunate in person in 1821.", "FALSE", "C", "Tadataka died three years before the final atlas was presented to the shogunate in 1821, leaving his apprentices to complete the delicate brushwork.", "He died three years earlier; his apprentices finished it."),
            ("British naval hydrographers purchased copies of Tadataka's maps in Nagasaki.", "NOT GIVEN", "B", "accurate enough to astonish British naval hydrographers decades later.", "Their reaction is mentioned, not a purchase in Nagasaki."),
        ],
        [
            ("Surveyors recorded daily map bearings onto handmade ________ paper.", ["mulberry"], "B", "transferred raw bearings onto handmade mulberry paper using fine bamboo dividers.", "Exact material word before 'paper'."),
            ("Tadataka checked latitude at night using a portable ________.", ["quadrant"], "B", "astronomical latitude measurements obtained through a portable quadrant.", "Exact instrument noun."),
            ("Modern ________ comparisons show his coastline mapping had remarkable accuracy.", ["satellite"], "C", "satellite overlays conducted in the twenty-first century confirm that his coastal contours deviate by less than one-thousandth of a degree", "Exact single modifier."),
        ],
    ),
]
