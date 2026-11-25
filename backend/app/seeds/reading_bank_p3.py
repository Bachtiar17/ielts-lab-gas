"""Original Academic Reading Drill Bank — Slot 3 (10 Passage-3 style drills).

Each drill features 4 abstract/argumentative paragraphs (A-D) with MCQ Single (Q1-Q2),
Yes/No/Not Given (Q3-Q4), and Short Answer (NO MORE THAN TWO WORDS AND/OR A NUMBER, Q5-Q6).
"""

from __future__ import annotations

from typing import Any


def _make_p3_drill(
    slug: str,
    title: str,
    subtitle: str,
    topic: str,
    paragraphs: list[tuple[str, str]],
    mcqs: list[tuple[str, list[tuple[str, str]], str, str, str, str]],
    ynngs: list[tuple[str, str, str, str, str]],
    shorts: list[tuple[str, list[str], str, str, str]],
) -> dict[str, Any]:
    wl = {"max_words": 2, "allow_number": True, "max_numbers": 1, "label": "NO MORE THAN TWO WORDS AND/OR A NUMBER"}
    questions: list[dict[str, Any]] = []
    for idx, (prompt, opts, ans, pid, quote, note) in enumerate(mcqs, start=1):
        questions.append(
            {
                "id": f"{slug}-q{idx:02d}",
                "passage_index": 1,
                "question_number": idx,
                "question_type": "mcq_single",
                "target_band": 7.5,
                "prompt_payload": {
                    "group_id": f"{slug}-g1",
                    "prompt": prompt,
                    "options": [{"id": oid, "text": otxt} for oid, otxt in opts],
                },
                "answer_key": {"accepted": [ans]},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    for offset, (prompt, ans, pid, quote, note) in enumerate(ynngs, start=3):
        questions.append(
            {
                "id": f"{slug}-q{offset:02d}",
                "passage_index": 1,
                "question_number": offset,
                "question_type": "ynng",
                "target_band": 7.5,
                "prompt_payload": {"group_id": f"{slug}-g2", "prompt": prompt},
                "answer_key": {"accepted": [ans]},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    for offset, (prompt, accepted, pid, quote, note) in enumerate(shorts, start=5):
        questions.append(
            {
                "id": f"{slug}-q{offset:02d}",
                "passage_index": 1,
                "question_number": offset,
                "question_type": "short_answer",
                "target_band": 8.0,
                "prompt_payload": {"group_id": f"{slug}-g3", "prompt": prompt, "word_limit": wl},
                "answer_key": {"accepted": accepted, "word_limit": wl},
                "evidence_span": {"paragraph_id": pid, "quote": quote, "distractor_note": note},
            }
        )
    return {
        "id": slug,
        "title": title,
        "subtitle": subtitle,
        "difficulty_label": "Passage 3 · Band 7.0–8.5",
        "duration_minutes": 20,
        "drill_slot": 3,
        "passages": [
            {
                "index": 1,
                "title": title,
                "subtitle": subtitle,
                "topic": topic,
                "recommended_minutes": 20,
                "paragraphs": [{"id": pid, "text": txt} for pid, txt in paragraphs],
                "question_groups": [
                    {
                        "id": f"{slug}-g1",
                        "title": "Questions 1–2",
                        "question_type": "mcq_single",
                        "instructions": "Choose the correct letter, A, B, C, or D.",
                        "question_numbers": [1, 2],
                    },
                    {
                        "id": f"{slug}-g2",
                        "title": "Questions 3–4",
                        "question_type": "ynng",
                        "instructions": "Do the following statements agree with the views of the writer? Choose YES, NO, or NOT GIVEN.",
                        "question_numbers": [3, 4],
                    },
                    {
                        "id": f"{slug}-g3",
                        "title": "Questions 5–6",
                        "question_type": "short_answer",
                        "instructions": "Answer the questions below. Choose NO MORE THAN TWO WORDS AND/OR A NUMBER from the passage.",
                        "word_limit": wl,
                        "question_numbers": [5, 6],
                    },
                ],
            }
        ],
        "questions": questions,
    }


P3_DRILLS: list[dict[str, Any]] = [
    _make_p3_drill(
        "drill-p3-01",
        "The Rebound Effect in Energy Efficiency",
        "Why making machines cheaper to run rarely cuts total consumption one-for-one",
        "Environmental Economics",
        [
            ("A", "In 1865, British economist William Stanley Jevons startled industrialists by noting that James Watt's dramatically more efficient steam engine had triggered a surge—not a drop—in national coal demand. Because cheaper mechanical power made steam viable across dozens of new textile mills and ironworks, efficiency lowered the effective price of energy services and expanded overall consumption. Economists still refer to this counterintuitive dynamic as the Jevons Paradox."),
            ("B", "Modern energy analysts distinguish between direct and indirect rebound effects. A household that replaces an old petrol sedan with a hybrid car may drive fifteen percent more kilometres each year because fuel feels cheaper per trip (direct rebound). Even if driving stays flat, spending the saved petrol money on weekend flights or heated home extensions shifts emissions elsewhere in the economy (indirect rebound)."),
            ("C", "Skeptics of efficiency mandates occasionally weaponize Jevons's observation to argue that engineering improvements are pointless. That conclusion overreaches badly: empirical meta-analyses show that in mature wealthy economies, direct rebound in household lighting and refrigeration typically erodes only ten to thirty percent of theoretical energy savings, leaving seventy percent or more intact."),
            ("D", "Policy scholars therefore contend that technological efficiency works best when paired with binding carbon caps or progressive energy pricing. Engineering innovation supplies the low-energy tools, while smart pricing ensures the resulting savings translate into genuine ecological relief rather than ever-larger consumption footprints."),
        ],
        [
            ("Why did coal consumption rise after James Watt's improved steam engine?", [("A", "Early engines leaked coal dust during transit"), ("B", "Lower operating costs opened up many new industrial uses"), ("C", "British law mandated minimum coal quotas"), ("D", "Ironworks rejected efficient boilers")], "B", "A", "Because cheaper mechanical power made steam viable across dozens of new textile mills and ironworks", "Lower effective cost expanded industrial adoption (B)."),
            ("What does the writer say about critics who claim efficiency standards are pointless?", [("A", "Their claim is confirmed by household fridge studies"), ("B", "They exaggerate rebound sizes in mature economies"), ("C", "They correctly reject carbon pricing"), ("D", "They rely too heavily on 19th-century textile data")], "B", "C", "That conclusion overreaches badly: empirical meta-analyses show that in mature wealthy economies, direct rebound in household lighting and refrigeration typically erodes only ten to thirty percent", "Writer explicitly refutes extreme pessimism (B)."),
        ],
        [
            ("Buying weekend flights with money saved on car fuel is an example of an indirect rebound effect.", "YES", "B", "spending the saved petrol money on weekend flights or heated home extensions shifts emissions elsewhere in the economy (indirect rebound).", "Matches Paragraph B directly."),
            ("Developing countries experience smaller direct rebound effects than wealthy European nations.", "NOT GIVEN", "C", "empirical meta-analyses show that in mature wealthy economies, direct rebound in household lighting and refrigeration typically erodes only ten to thirty percent", "Developing economies are never compared."),
        ],
        [
            ("What is the classic economic term for efficiency leading to higher overall resource use?", ["Jevons Paradox", "the Jevons Paradox"], "A", "Economists still refer to this counterintuitive dynamic as the Jevons Paradox.", "Two-word eponymous term."),
            ("At least what percentage of theoretical savings usually remains intact in household lighting and refrigeration?", ["70%", "seventy percent", "70 percent"], "C", "leaving seventy percent or more intact.", "Tests numeric equivalence and word limit."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-02",
        "The Limits of Metric-Driven Science",
        "When citation counts become targets, Goodhart's Law reshapes academic discovery",
        "Philosophy of Science",
        [
            ("A", "Funding agencies understandably crave objective yardsticks when distributing scarce grant budgets across thousands of competing laboratories. Over the past forty years, quantitative bibliometrics—journal impact factors, annual paper counts, and h-index scores—have moved from modest library-cataloguing aids to decisive gatekeepers of academic careers."),
            ("B", "Yet sociologist Marilyn Strathern's formulation of Goodhart's Law warns that 'when a measure becomes a target, it ceases to be a good measure'. Once promotion committees reward publication volume and rapid citation velocity, researchers face intense pressure to slice single findings into multiple 'least publishable units' and chase trendy incremental questions rather than slow, high-risk breakthroughs."),
            ("C", "Equally troubling is the distortion of replication work. Verifying an existing landmark claim rarely earns prestigious journal covers or dramatic citation bursts, even though independent replication forms the bedrock of reliable empirical knowledge. Abandoning quantitative indicators completely, however, would invite back the opaque old-boy patronage networks that metrics originally helped curb."),
            ("D", "Reformers behind the San Francisco Declaration on Research Assessment advocate a hybrid model: pairing transparent narrative CVs—where scientists explain the real-world impact of their five strongest contributions—with bounded bibliometrics stripped of journal-level prestige shortcuts."),
        ],
        [
            ("What was the original role of bibliometric indicators mentioned in Paragraph A?", [("A", "Ranking university teaching quality"), ("B", "Modest tools for cataloguing library holdings"), ("C", "Detecting fabricated laboratory datasets"), ("D", "Replacing peer review at medical journals")], "B", "A", "have moved from modest library-cataloguing aids to decisive gatekeepers of academic careers.", "Matches Paragraph A."),
            ("Why does the writer warn against abandoning quantitative metrics altogether?", [("A", "Narrative CVs take too long for computers to scan"), ("B", "Informal patronage biases could return unchecked"), ("C", "Replication studies require high impact factors"), ("D", "Bibliometrics predict Nobel prizes accurately")], "B", "C", "Abandoning quantitative indicators completely, however, would invite back the opaque old-boy patronage networks that metrics originally helped curb.", "Captures the balanced concession in Paragraph C."),
        ],
        [
            ("Rewarding rapid citation counts encourages researchers to prioritize cautious, incremental studies over risky long-term inquiries.", "YES", "B", "chase trendy incremental questions rather than slow, high-risk breakthroughs.", "Directly agrees with Paragraph B."),
            ("Independent replication studies are currently funded at higher rates than novel exploratory grants.", "NO", "C", "Verifying an existing landmark claim rarely earns prestigious journal covers or dramatic citation bursts", "Wait—let's check carefully: Paragraph C discusses journal prestige/citations, not funding rates! Better make this statement match Paragraph C directly -> NO? Actually funding rate isn't stated; let's check our quote!"),
        ],
        [
            ("What phrase describes splitting one discovery into several tiny papers?", ["least publishable", "publishable units"], "B", "slice single findings into multiple 'least publishable units'", "Wait—3 words! Let's ask a clean 2-word question."),
            ("How many top works do scientists highlight under the narrative CV reform described?", ["five", "5"], "D", "explain the real-world impact of their five strongest contributions", "Tests numeric equivalence."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-03",
        "Bilingualism and Executive Attention",
        "Debating whether juggling two languages fortifies the brain's control network",
        "Psycholinguistics",
        [
            ("A", "For much of the twentieth century, educational psychologists worried that exposing young children to two languages simultaneously would induce linguistic confusion and slow vocabulary growth. Neuroimaging has decisively overturned that fear: both language systems remain simultaneously active inside a bilingual brain, requiring constant mental selection without harming core comprehension."),
            ("B", "Building on this discovery, psychologist Ellen Bialystok proposed the 'bilingual advantage' hypothesis, arguing that lifelong practice inhibiting one language while speaking another trains domain-general executive control—skills such as task switching and ignoring visual distractors. Early small-sample laboratory experiments appeared to confirm faster reaction times among bilingual elders."),
            ("C", "Over the past decade, however, large-scale replication studies involving thousands of participants have produced far messier results, frequently finding negligible differences between monolinguals and bilinguals on standard colour-word Stroop tests. Critics point out that publication bias favoured dramatic positive findings while quietly burying null studies in file drawers."),
            ("D", "Contemporary psycholinguists increasingly view the debate as overly binary. Rather than asking whether bilingualism grants a universal cognitive boost, researchers now examine interactional context: speakers who constantly switch languages within the same conversation show sharper attentional flexibility than dual-language speakers who keep each language strictly compartmentalized at home versus work."),
        ],
        [
            ("What does Paragraph C suggest helped exaggerate early claims of a universal bilingual advantage?", [("A", "Faulty neuroimaging scanners"), ("B", "Selective publication of positive results over null findings"), ("C", "Monolinguals refusing to take Stroop tests"), ("D", "Bilinguals speaking too slowly in interviews")], "B", "C", "Critics point out that publication bias favoured dramatic positive findings while quietly burying null studies in file drawers.", "Matches publication bias (B)."),
            ("According to Paragraph D, which bilinguals show the strongest attentional flexibility?", [("A", "Adults who learned a second language strictly from textbooks"), ("B", "Speakers who alternate frequently between languages in shared settings"), ("C", "Children who keep home and school languages completely separate"), ("D", "Elderly speakers who stopped using their first language")], "B", "D", "speakers who constantly switch languages within the same conversation show sharper attentional flexibility than dual-language speakers who keep each language strictly compartmentalized", "Directly matches B."),
        ],
        [
            ("Twentieth-century fears that childhood bilingualism impairs core comprehension have been disproved.", "YES", "A", "Neuroimaging has decisively overturned that fear: both language systems remain simultaneously active inside a bilingual brain, requiring constant mental selection without harming core comprehension.", "Directly agrees with Paragraph A."),
            ("The writer believes the 'bilingual advantage' question is best framed as a simple yes-or-no verdict.", "NO", "D", "Contemporary psycholinguists increasingly view the debate as overly binary.", "Writer endorses moving beyond a binary framing."),
        ],
        [
            ("Which classic laboratory task is mentioned as showing negligible differences in large replications?", ["Stroop tests", "Stroop test"], "C", "frequently finding negligible differences between monolinguals and bilinguals on standard colour-word Stroop tests.", "Fits NO MORE THAN TWO WORDS."),
            ("What mental faculty did Bialystok argue is strengthened by inhibiting a second language?", ["executive control"], "B", "trains domain-general executive control—skills such as task switching", "Exact two-word term."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-04",
        "Why Forecasting Models Struggle with Fat Tails",
        "Distinguishing tame bell-curve averages from wild extremes in complex systems",
        "Statistical Thinking",
        [
            ("A", "Human height, factory bolt diameters, and seasonal rainfall totals cluster neatly around a stable mean; an outlier ten times larger than average is physically impossible. Statisticians label such domains 'mild randomness', where standard bell curves allow insurers and engineers to forecast risk with extraordinary precision."),
            ("B", "Financial crashes, viral pandemics, and wildfire acreage obey an altogether different mathematical regime known as 'fat-tailed' distributions. In these interconnected systems, a single extreme event can outweigh the combined impact of the previous thousand ordinary observations, rendering simple historical averages dangerously misleading."),
            ("C", "Decision theorists note that institutional planners repeatedly import bell-curve intuition into fat-tailed arenas because tidy single-number forecasts reassure boards and voters. When a river levee is engineered strictly for a 'hundred-year flood' estimated from fifty years of calm gauges, hidden tail risk accumulates silently until a single storm breaches the entire grid."),
            ("D", "Risk experts therefore advocate shifting from brittle point prediction toward 'stress-tested robustness': designing supply chains, power grids, and financial buffers to absorb extreme shocks without catastrophic collapse, even when the exact timing of the next tail event remains fundamentally unknowable."),
        ],
        [
            ("What distinguishes a fat-tailed domain from mild randomness?", [("A", "Measurements cluster tightly around a stable average"), ("B", "One extreme outlier can dominate the total cumulative outcome"), ("C", "Historical records are always completely unavailable"), ("D", "Bell curves predict viral outbreaks accurately")], "B", "B", "a single extreme event can outweigh the combined impact of the previous thousand ordinary observations", "Matches B."),
            ("Why do institutions persist in using single-number bell-curve forecasts in complex systems?", [("A", "Clean forecasts offer psychological reassurance to stakeholders"), ("B", "Regulators prohibit stress-testing supply chains"), ("C", "Computers cannot simulate fat-tailed distributions"), ("D", "Fifty years of data always captures every extreme flood")], "A", "C", "because tidy single-number forecasts reassure boards and voters.", "Directly stated in Paragraph C."),
        ],
        [
            ("Human height is an example of a domain where bell-curve statistics work reliably.", "YES", "A", "Statisticians label such domains 'mild randomness', where standard bell curves allow insurers and engineers to forecast risk with extraordinary precision.", "Confirmed in Paragraph A."),
            ("With enough computing power, analysts can predict the exact date of the next financial tail event.", "NO", "D", "even when the exact timing of the next tail event remains fundamentally unknowable.", "Contradicts 'fundamentally unknowable'."),
        ],
        [
            ("What two-word term describes tame domains where bell curves reliably forecast risk?", ["mild randomness"], "A", "Statisticians label such domains 'mild randomness'", "Exact two-word term."),
            ("How many years of calm gauge records are cited in the levee example?", ["50", "fifty", "50 years", "fifty years"], "C", "estimated from fifty years of calm gauges", "Tests number equivalence and word limit."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-05",
        "The Psychology of Algorithmic Aversion",
        "Why people forgive human errors faster than identical mistakes made by software",
        "Behavioral Decision Science",
        [
            ("A", "Across medical triage, weather forecasting, and loan underwriting, statistical algorithms consistently match or outperform unaided human experts on average accuracy. Yet behavioral economists Berkeley Dietvorst and colleagues uncovered a striking asymmetry: once people watch an algorithm make a single visible mistake, they abandon it far more rapidly than they abandon a human advisor committing the exact same error."),
            ("B", "Researchers term this bias 'algorithmic aversion'. Because observers intuitively believe human experts learn from feedback and exercise flexible judgment, they treat human blunders as fixable slips; by contrast, a flawed computer prediction feels like proof of a rigid, permanently broken rulebook."),
            ("C", "Intriguingly, Dietvorst's follow-up trials uncovered a remarkably simple remedy. When study participants were permitted to tweak a forecasting model's output—even when their adjustments were strictly capped at a tiny two-percent margin—willingness to rely on the algorithm surged dramatically and overall decision accuracy rose."),
            ("D", "Designers of clinical and aviation decision aids draw a vital lesson from these experiments: completely automated black boxes breed distrust and workaround behaviour. Preserving meaningful human-in-the-loop agency—allowing practitioners to inspect reasoning and make bounded adjustments—captures statistical accuracy without triggering psychological rejection."),
        ],
        [
            ("Why do observers judge algorithmic errors more harshly than identical human mistakes?", [("A", "Algorithms are slower to generate predictions"), ("B", "Software errors appear systemic and uncorrectable compared with human slips"), ("C", "Human advisors rarely make mistakes in weather forecasting"), ("D", "Statistical models hide their accuracy scores")], "B", "B", "they treat human blunders as fixable slips; by contrast, a flawed computer prediction feels like proof of a rigid, permanently broken rulebook.", "Captures the psychological asymmetry (B)."),
            ("What happened when participants were allowed tiny bounded adjustments to a model's output?", [("A", "Decision accuracy collapsed due to human bias"), ("B", "Trust in the algorithm rose sharply alongside accuracy"), ("C", "Participants ignored the algorithm completely"), ("D", "The trial had to be halted for aviation safety")], "B", "C", "willingness to rely on the algorithm surged dramatically and overall decision accuracy rose.", "Directly matches B."),
        ],
        [
            ("Statistical models frequently achieve equal or better average accuracy than unaided human experts.", "YES", "A", "statistical algorithms consistently match or outperform unaided human experts on average accuracy.", "Directly stated in Paragraph A."),
            ("Fully automated black-box systems are the best way to gain clinician trust in hospitals.", "NO", "D", "completely automated black boxes breed distrust and workaround behaviour.", "Contradicted by Paragraph D."),
        ],
        [
            ("What two-word term names people's tendency to abandon software quickly after seeing an error?", ["algorithmic aversion"], "B", "Researchers term this bias 'algorithmic aversion'.", "Exact two-word term."),
            ("What maximum adjustment margin was still enough to boost user acceptance in Dietvorst's trials?", ["2%", "two-percent", "two percent"], "C", "strictly capped at a tiny two-percent margin", "Tests hyphenated word / number equivalence."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-06",
        "The Paradox of Choice in Everyday Markets",
        "When abundant options enhance autonomy—and when they induce decision paralysis",
        "Consumer Psychology",
        [
            ("A", "Classical microeconomics assumes that adding options to a marketplace can never make rational consumers worse off: anyone who dislikes the new entries can simply ignore them. Challenging that assumption, psychologist Barry Schwartz popularized the 'paradox of choice', arguing that excessive variety triggers cognitive overload, buyer's remorse, and procrastination."),
            ("B", "The thesis gained fame from a 2000 supermarket experiment in California: shoppers encountered either a tasting booth displaying twenty-four exotic jams or a modest table showing six. Although the larger display attracted more curious browsers, thirty percent of visitors to the six-jam booth bought a jar compared with barely three percent at the twenty-four-jam table."),
            ("C", "Subsequent meta-analyses of nearly a hundred choice-overload studies painted a more nuanced portrait. Choice paralysis is NOT automatic; it emerges primarily when consumers lack clear prior preferences, face hard-to-compare technical attributes, or fear making a socially regrettable mistake. Expert hobbyists browsing familiar categories often relish vast catalogues."),
            ("D", "Digital product architects therefore focus less on arbitrarily shrinking inventories and more on structured choice architecture—curated defaults, clear comparison filters, and staged narrowing—so novices feel guided while connoisseurs retain full breadth."),
        ],
        [
            ("In the 2000 jam experiment, how did the 24-jam display compare with the 6-jam display?", [("A", "It attracted fewer passersby and fewer buyers"), ("B", "It drew more browsers but converted far fewer into buyers"), ("C", "It outsold the smaller booth ten to one"), ("D", "Shoppers complained the exotic jams were too expensive")], "B", "B", "Although the larger display attracted more curious browsers, thirty percent of visitors to the six-jam booth bought a jar compared with barely three percent at the twenty-four-jam table.", "Directly matches B."),
            ("What did later meta-analyses reveal about choice overload?", [("A", "It affects expert hobbyists more severely than novices"), ("B", "It depends heavily on consumer expertise and attribute complexity"), ("C", "It occurs identically across every retail category"), ("D", "Supermarket displays are immune to decision paralysis")], "B", "C", "Choice paralysis is NOT automatic; it emerges primarily when consumers lack clear prior preferences, face hard-to-compare technical attributes, or fear making a socially regrettable mistake.", "Matches B."),
        ],
        [
            ("Classical microeconomic theory predicts that extra product choices should never harm rational buyers.", "YES", "A", "Classical microeconomics assumes that adding options to a marketplace can never make rational consumers worse off", "Confirmed in Paragraph A."),
            ("Online platforms should permanently delete rare items from their catalogues to prevent overload.", "NO", "D", "focus less on arbitrarily shrinking inventories and more on structured choice architecture", "Writer favours structured filtering over shrinking catalogues."),
        ],
        [
            ("What percentage of shoppers at the six-jam booth purchased a jar?", ["30%", "thirty percent", "30 percent"], "B", "thirty percent of visitors to the six-jam booth bought a jar", "Tests numeric equivalence."),
            ("What two-word design approach helps novices navigate large digital catalogues?", ["choice architecture"], "D", "more on structured choice architecture—curated defaults, clear comparison filters", "Exact two-word term."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-07",
        "Silent Intervals in Musical Cognition",
        "Why strategic pauses shape emotional anticipation as powerfully as played notes",
        "Music Neuroscience",
        [
            ("A", "Lay listeners commonly define music by its acoustic ingredients—melody, harmony, rhythm, and timbre—treating silence merely as empty backdrop between phrases. Musicologists and neuroscientists argue the opposite: calibrated rests are active structural instruments that sculpt expectation, tension, and emotional release."),
            ("B", "Electroencephalography experiments show that when a familiar melodic cadence halts unexpectedly just before its resolving tonic chord, the listener's auditory cortex does not drop to baseline stillness. Instead, neural predictive circuits fire vigorously during the silent gap, mentally projecting the missing pitch and heightening physiological arousal when the delayed note finally arrives."),
            ("C", "Cultural traditions deploy silence in distinct expressive ways. In classical Japanese shakuhachi flute music, the aesthetic principle of ma treats unhurried breath pauses as equal partners to sound, inviting contemplative stillness rather than dramatic suspense. Western symphonic composers like Beethoven, conversely, often weaponized sudden full-orchestra cutoffs to jolt audiences out of rhythmic complacency."),
            ("D", "Modern streaming playlists compressed for constant background listening increasingly trim quiet dynamic passages and shorten inter-track gaps. Acoustic researchers worry that eliminating dynamic contrast flattens the very predictive play between sound and silence that gives live music its goosebump-inducing power."),
        ],
        [
            ("What happens in the auditory cortex during an unexpected silent pause before a musical resolution?", [("A", "Neural activity shuts down completely until sound resumes"), ("B", "Predictive brain circuits actively anticipate the missing note"), ("C", "Listeners forget the preceding melody within seconds"), ("D", "Physiological arousal drops rapidly")], "B", "B", "neural predictive circuits fire vigorously during the silent gap, mentally projecting the missing pitch", "Matches B."),
            ("How does Paragraph C contrast Japanese shakuhachi music with Beethoven's symphonies?", [("A", "Beethoven avoided using silence in orchestral scores"), ("B", "Shakuhachi uses pauses for calm reflection whereas Beethoven used sudden cutoffs for dramatic shock"), ("C", "Both traditions strictly prohibit breath pauses"), ("D", "Japanese composers borrowed the concept of ma from Vienna")], "B", "C", "Western symphonic composers like Beethoven, conversely, often weaponized sudden full-orchestra cutoffs to jolt audiences out of rhythmic complacency.", "Matches B."),
        ],
        [
            ("Silence in music should be understood merely as passive empty space between notes.", "NO", "A", "Musicologists and neuroscientists argue the opposite: calibrated rests are active structural instruments", "Directly contradicts Paragraph A."),
            ("Streaming platforms earn higher ad revenue when inter-track pauses are removed.", "NOT GIVEN", "D", "Modern streaming playlists compressed for constant background listening increasingly trim quiet dynamic passages", "Ad revenue is never mentioned."),
        ],
        [
            ("What Japanese aesthetic concept treats unhurried pauses as equal partners to sound?", ["ma"], "C", "the aesthetic principle of ma treats unhurried breath pauses as equal partners to sound", "Single exact term."),
            ("Which brain-imaging technique revealed active predictive firing during musical silences?", ["Electroencephalography", "EEG"], "B", "Electroencephalography experiments show that when a familiar melodic cadence halts unexpectedly", "Exact single word."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-08",
        "The Shifting Baseline Syndrome in Conservation",
        "Why each human generation mistakes an impoverished ecosystem for pristine nature",
        "Conservation Psychology",
        [
            ("A", "In 1995, fisheries scientist Daniel Pauly coined the term 'shifting baseline syndrome' to describe a quiet generational amnesia warping marine conservation. Each cohort of fisheries biologists naturally treats the fish abundance witnessed at the start of their own career as the 'normal' benchmark, gradually normalizing catastrophic multi-century depletion."),
            ("B", "Archival menus, ship logbooks, and nineteenth-century trophy photographs expose how dramatically baselines have drifted. Along the Florida Keys, giant goliath groupers weighing over two hundred kilograms were routine dockside catches in the 1950s; by the 2000s, recreational anglers celebrated catching fish a tenth that size, unaware of the giants their grandparents once hauled ashore."),
            ("C", "Environmental psychologists warn that shifting baselines erode public urgency for ambitious restoration. Citizens who grow up beside silent, songbird-poor suburbs or murky rivers feel little sense of loss because they never experienced abundant wetlands firsthand—a phenomenon researchers label 'environmental generational amnesia'."),
            ("D", "Countering historical myopia demands pairing modern ecological surveys with historical ecology—oral histories from elder fishers, archaeological fish-bone middens, and museum herbarium sheets—so restoration targets aim for genuine biological vitality rather than merely preserving yesterday's already degraded remnant."),
        ],
        [
            ("What caused fisheries scientists to underestimate long-term ocean depletion according to Pauly?", [("A", "Deliberate falsification of catch logs"), ("B", "Treating depleted ecosystems from their own youth as the natural standard"), ("C", "Focusing exclusively on freshwater rivers"), ("D", "Ignoring satellite ocean temperature maps")], "B", "A", "Each cohort of fisheries biologists naturally treats the fish abundance witnessed at the start of their own career as the 'normal' benchmark", "Matches B."),
            ("Why do conservationists recommend using elder oral histories and archaeological middens?", [("A", "Modern satellite cameras cannot detect fish"), ("B", "They reconstruct richer historical targets for ecological restoration"), ("C", "Museum specimens are cheaper than ocean boats"), ("D", "They prove ancient fishing caused grouper extinction")], "B", "D", "so restoration targets aim for genuine biological vitality rather than merely preserving yesterday's already degraded remnant.", "Matches B."),
        ],
        [
            ("Anglers in the Florida Keys in the 2000s generally knew how huge grouper catches had been in the 1950s.", "NO", "B", "recreational anglers celebrated catching fish a tenth that size, unaware of the giants their grandparents once hauled ashore.", "Explicitly states they were 'unaware'."),
            ("Experiencing degraded landscapes from childhood can weaken public motivation to support bold restoration.", "YES", "C", "Environmental psychologists warn that shifting baselines erode public urgency for ambitious restoration.", "Confirmed in Paragraph C."),
        ],
        [
            ("In what year did Daniel Pauly introduce the term 'shifting baseline syndrome'?", ["1995"], "A", "In 1995, fisheries scientist Daniel Pauly coined the term 'shifting baseline syndrome'", "Single year number."),
            ("What discipline combines elder memories, middens, and museum archives with modern surveys?", ["historical ecology"], "D", "pairing modern ecological surveys with historical ecology", "Exact two-word discipline name."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-09",
        "Desirable Difficulties in Human Learning",
        "Why effortless rereading creates fluency illusions while spaced retrieval builds mastery",
        "Educational Neuroscience",
        [
            ("A", "Ask university students how they prepare for high-stakes exams, and the vast majority describe highlighting textbook chapters and rereading notes repeatedly until every paragraph feels familiar. Paradoxically, decades of memory experiments prove that this sense of smooth familiarity—called an 'illusion of competence'—is one of the weakest predictors of durable recall a week later."),
            ("B", "Cognitive psychologists Robert and Elizabeth Bjork coined the term 'desirable difficulties' to explain why conditions that feel slower and more frustrating during study actually yield vastly stronger long-term retention. Spacing practice across multiple days, interleaving mixed problem types, and forcing active retrieval without peeking at notes compel the brain to reconstruct neural pathways rather than passively recognizing ink."),
            ("C", "Crucially, not every obstacle qualifies as desirable. Presenting opaque jargon to a complete beginner or removing worked examples before core grammar is understood creates 'undesirable difficulty' that simply triggers cognitive overload and abandonment. Effective challenge sits right at the edge of current mastery—effortful, yet solvable."),
            ("D", "Instructional designers therefore argue that learners need explicit metacognitive coaching so they stop mistaking effortless study sessions for productive ones. When students understand *why* struggling through a low-stakes practice quiz beats highlighting a page twice, they persist through productive friction."),
        ],
        [
            ("Why is repeated rereading an unreliable indicator of long-term exam readiness?", [("A", "It increases stress hormones during lectures"), ("B", "Familiarity on the page feels like mastery without strengthening retrieval"), ("C", "Highlighting destroys ink contrast in textbooks"), ("D", "Memory experiments show rereading harms short-term recognition")], "B", "A", "this sense of smooth familiarity—called an 'illusion of competence'—is one of the weakest predictors of durable recall a week later.", "Matches B."),
            ("According to Paragraph C, what separates desirable difficulty from undesirable difficulty?", [("A", "Desirable difficulty involves timed high-stakes exams"), ("B", "Desirable difficulty is effortful yet achievable given a learner's foundation"), ("C", "Undesirable difficulty only occurs in mathematics"), ("D", "Worked examples always create undesirable difficulty")], "B", "C", "Effective challenge sits right at the edge of current mastery—effortful, yet solvable.", "Matches B."),
        ],
        [
            ("Mixing different problem types during practice tends to feel harder in the moment but improves retention.", "YES", "B", "conditions that feel slower and more frustrating during study actually yield vastly stronger long-term retention. Spacing practice across multiple days, interleaving mixed problem types", "Confirmed in Paragraph B."),
            ("University professors receive mandatory training in the Bjorks' framework across Europe.", "NOT GIVEN", "D", "Instructional designers therefore argue that learners need explicit metacognitive coaching", "Professor training mandates in Europe are never mentioned."),
        ],
        [
            ("What two-word phrase did Robert and Elizabeth Bjork coin for productive learning friction?", ["desirable difficulties"], "B", "coined the term 'desirable difficulties' to explain why conditions that feel slower", "Exact two-word term."),
            ("What kind of coaching do instructional designers recommend so students value productive struggle?", ["metacognitive coaching", "metacognitive"], "D", "learners need explicit metacognitive coaching so they stop mistaking effortless study sessions", "Fits NO MORE THAN TWO WORDS."),
        ],
    ),
    _make_p3_drill(
        "drill-p3-10",
        "The Philosophy of Repairability and Planned Obsolescence",
        "How glued enclosures and software locks reshaped consumers' relationship with objects",
        "Technology & Society",
        [
            ("A", "Mid-twentieth-century household radios and sewing machines routinely shipped with printed circuit schematics tucked inside the back cover, inviting owners or neighbourhood technicians to swap worn capacitors with a simple screwdriver. Over the past two decades, sleek smartphones and cordless appliances have increasingly replaced standard screws with structural adhesives, proprietary fasteners, and serial-paired software locks."),
            ("B", "Manufacturers defend sealed architectures as indispensable for waterproofing, wafer-thin ergonomics, and electrical safety. Right-to-repair advocates counter that design choices often go well beyond physical necessity: when a three-dollar battery is permanently glued beneath a fragile display screen, routine chemical aging transforms a functional thousand-dollar computer into premature electronic waste."),
            ("C", "Economists examining 'modular repairability' note that extending average smartphone lifespans by just two years could eliminate millions of tonnes of carbon emissions tied to rare-earth mining and semiconductor fabrication. Yet voluntary green marketing has achieved little, because shorter replacement cycles remain financially lucrative when disposal externalities sit off corporate balance sheets."),
            ("D", "Recent European eco-design mandates—requiring accessible spare parts, standardized battery removal, and repairability score labels at retail checkout—signal a structural shift. When repair scores sit visibly beside price tags, durability stops being an invisible engineering footnote and becomes a competitive marketplace feature."),
        ],
        [
            ("What evidence in Paragraph A shows that mid-century manufacturers expected owners to fix devices?", [("A", "Appliances carried lifetime factory replacement guarantees"), ("B", "Printed circuit diagrams were included inside the product casing"), ("C", "Governments subsidized neighbourhood radio shops"), ("D", "Devices were built using waterproof structural adhesives")], "B", "A", "routinely shipped with printed circuit schematics tucked inside the back cover, inviting owners or neighbourhood technicians to swap worn capacitors", "Matches B."),
            ("Why has voluntary green marketing failed to lengthen smartphone lifespans according to Paragraph C?", [("A", "Consumers prefer glued batteries for safety"), ("B", "Rapid replacement stays profitable when waste costs are externalized"), ("C", "Rare-earth mining emits negligible carbon"), ("D", "Modular phones cannot run modern operating systems")], "B", "C", "because shorter replacement cycles remain financially lucrative when disposal externalities sit off corporate balance sheets.", "Matches B."),
        ],
        [
            ("Manufacturers argue that sealed designs help achieve water resistance and slim profiles.", "YES", "B", "Manufacturers defend sealed architectures as indispensable for waterproofing, wafer-thin ergonomics, and electrical safety.", "Directly stated in Paragraph B."),
            ("Visible repairability scores at checkout are unlikely to influence consumer competition.", "NO", "D", "When repair scores sit visibly beside price tags, durability stops being an invisible engineering footnote and becomes a competitive marketplace feature.", "Writer argues the exact opposite."),
        ],
        [
            ("By how many years would extending smartphone lifespans cut millions of tonnes of emissions?", ["2", "two", "2 years", "two years"], "C", "extending average smartphone lifespans by just two years could eliminate millions of tonnes of carbon emissions", "Tests numeric equivalence."),
            ("What checkout labels are highlighted in recent European eco-design rules?", ["repairability score", "repair scores"], "D", "requiring accessible spare parts, standardized battery removal, and repairability score labels at retail checkout", "Fits NO MORE THAN TWO WORDS."),
        ],
    ),
]


# Quick polish on drill-p3-02 Q4 & Q5 so they are 100% airtight against verbatim text!
P3_DRILLS[1]["questions"][3]["prompt_payload"]["prompt"] = (
    "Replicating a landmark study frequently wins prestigious journal covers."
)
P3_DRILLS[1]["questions"][3]["answer_key"]["accepted"] = ["NO"]
P3_DRILLS[1]["questions"][3]["evidence_span"]["distractor_note"] = (
    "Paragraph C explicitly states that verifying an existing claim 'rarely earns prestigious journal covers'."
)
P3_DRILLS[1]["questions"][4]["prompt_payload"]["prompt"] = (
    "Whose formulation of Goodhart's Law is quoted in Paragraph B?"
)
P3_DRILLS[1]["questions"][4]["answer_key"]["accepted"] = ["Marilyn Strathern", "Strathern"]
P3_DRILLS[1]["questions"][4]["evidence_span"]["quote"] = (
    "Yet sociologist Marilyn Strathern's formulation of Goodhart's Law warns that 'when a measure becomes a target, it ceases to be a good measure'."
)
P3_DRILLS[1]["questions"][4]["evidence_span"]["distractor_note"] = (
    "Fits NO MORE THAN TWO WORDS: 'Marilyn Strathern' or 'Strathern'."
)
