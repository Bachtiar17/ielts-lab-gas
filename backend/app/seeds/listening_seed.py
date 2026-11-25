"""Original 4-Part (40-Question) IELTS Academic Listening Mock Test Seed.

Follows the official post-2020 IDP IELTS Academic Listening format (Parts 1-4, NO Part 1 spoken example):
- Part 1 (Q1-Q10): Everyday social conversation (2 speakers) — Form/Note completion with self-corrections & spelled details.
- Part 2 (Q11-Q20): Everyday social monologue — Interactive SVG Map Labelling (Q11-Q15) + MCQ Single (Q16-Q20).
- Part 3 (Q21-Q30): Academic tutorial discussion (3 speakers) — MCQ Single (Q21-Q25) + Matching (Q26-Q30).
- Part 4 (Q31-Q40): Academic lecture monologue — Structured Lecture Note Completion (ONE WORD ONLY).

100% original scripts, questions, and SVG map coordinates — zero copyrighted material.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.app.db.models import ListeningTest, QuestionItem

LISTENING_TEST_ID = "acad-listening-mock-01"

LISTENING_PARTS: list[dict[str, Any]] = [
    {
        "index": 1,
        "title": "Part 1 — Coastal Rowing Club Membership Enquiry",
        "context": "Everyday social conversation between a club coordinator (Claire) and a prospective member (David).",
        "speakers": [
            {"speaker": "Claire", "voice": "Kore", "accent": "UK English", "role": "Club Coordinator"},
            {"speaker": "David", "voice": "Puck", "accent": "AU English", "role": "Applicant"},
        ],
        "audio_filename": "listening_01_part1.wav",
        "transcript": [
            {"id": "p1-t1", "speaker": "Claire", "style": "warm and professional", "text": "Good morning, Bayview Coastal Rowing Club, Claire speaking. How can I help you today?"},
            {"id": "p1-t2", "speaker": "David", "style": "friendly and curious", "text": "Hi Claire, I just moved to the harbour area and I'd love to sign up for the beginner rowing sessions."},
            {"id": "p1-t3", "speaker": "Claire", "style": "helpful", "text": "Wonderful! Let me take a few details for your provisional form. Could I have your full name, please?"},
            {"id": "p1-t4", "speaker": "David", "style": "clear", "text": "Sure, it's David Hargreaves. That's spelled H-A-R-G-R-E-A-V-E-S."},
            {"id": "p1-t5", "speaker": "Claire", "style": "attentive", "text": "Got it, David Hargreaves. And what's your local postcode so we can mail your boathouse pass?"},
            {"id": "p1-t6", "speaker": "David", "style": "natural", "text": "I'm still unpacking so let me check—oh yes, it's BH14 7QR."},
            {"id": "p1-t7", "speaker": "Claire", "style": "helpful", "text": "BH14 7QR, lovely. Now, for new adult members, our standard annual fee used to be 140 pounds, but since we added indoor ergometer access this season, it's now 165 pounds—or you can try a six-week starter pass for 45 pounds."},
            {"id": "p1-t8", "speaker": "David", "style": "decisive", "text": "Let's start with the six-week starter pass, please, just to see how my schedule settles."},
            {"id": "p1-t9", "speaker": "Claire", "style": "informative", "text": "Smart choice, 45 pounds it is. Next, let's book your mandatory safety induction. We normally run those on Thursday mornings, oh wait—our slipway is being resurfaced this Thursday, so this week's induction has moved to Saturday the 14th of July."},
            {"id": "p1-t10", "speaker": "David", "style": "confirming", "text": "Saturday the 14th of July works even better for me. What time should I arrive at the boathouse?"},
            {"id": "p1-t11", "speaker": "Claire", "style": "clear", "text": "Water launch is at ten o'clock sharp, so please arrive by 9:30 am for your lifejacket fitting and briefing."},
            {"id": "p1-t12", "speaker": "David", "style": "curious", "text": "Great, 9:30 am. Do I need to bring any specialized kit?"},
            {"id": "p1-t13", "speaker": "Claire", "style": "practical", "text": "We supply oars and flotation vests. Avoid baggy cotton hoodies because they snag on sliding seats—wear close-fitting athletic layers, and bring old waterproof sandals or neoprene booties, plus a reusable bottle of water and strong sunscreen."},
            {"id": "p1-t14", "speaker": "David", "style": "thoughtful", "text": "Got it—waterproof sandals and sunscreen. Should I mention that I did a little kayaking at university, or is this strictly from scratch?"},
            {"id": "p1-t15", "speaker": "Claire", "style": "encouraging", "text": "Do mention your kayaking—it helps our coach pair crews evenly. One quick health check: can you swim at least fifty metres in light clothing without a float?"},
            {"id": "p1-t16", "speaker": "David", "style": "confident", "text": "Yes, easily. Where is the best place to park if I drive down?"},
            {"id": "p1-t17", "speaker": "Claire", "style": "helpful", "text": "The main pier car park fills up with ferry commuters, so turn just before the lighthouse onto Marina Lane—members get two hours of free parking behind the old bakery."},
            {"id": "p1-t18", "speaker": "David", "style": "grateful", "text": "Behind the old bakery on Marina Lane—thanks so much, Claire! Oh, and what's the best email if the weather turns rough?"},
            {"id": "p1-t19", "speaker": "Claire", "style": "warm", "text": "If winds top twenty knots, we post an alert on our club app and text you directly. For general questions, email crew@bayviewrowing.org—and ask for Coach Martin if you arrive early."},
        ],
        "question_groups": [
            {
                "id": "l1-p1-g1",
                "title": "Questions 1–10",
                "question_type": "form_note_table_completion",
                "instructions": "Complete the membership enquiry form below. Write ONE WORD AND/OR A NUMBER for each answer.",
                "word_limit": {
                    "max_words": 1,
                    "allow_number": True,
                    "max_numbers": 2,
                    "label": "ONE WORD AND/OR A NUMBER",
                },
                "note_heading": "Bayview Coastal Rowing Club — Beginner Enquiry Form",
                "question_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            }
        ],
    },
    {
        "index": 2,
        "title": "Part 2 — Harbourview Maritime Museum Orientation",
        "context": "Everyday social monologue by a museum curator welcoming visitors to the newly renovated waterfront complex.",
        "speakers": [
            {"speaker": "Curator", "voice": "Charon", "accent": "UK English", "role": "Museum Curator"},
        ],
        "audio_filename": "listening_01_part2.wav",
        "map_data": {
            "title": "Harbourview Maritime Museum — Ground Floor & Courtyard",
            "compass": "North is at the top",
            "landmarks": [
                {"label": "MAIN ENTRANCE (South)", "x": 260, "y": 330, "w": 160, "h": 34, "kind": "anchor"},
                {"label": "TICKET FOYER", "x": 260, "y": 260, "w": 160, "h": 54, "kind": "anchor"},
                {"label": "CENTRAL COURTYARD", "x": 250, "y": 140, "w": 180, "h": 98, "kind": "courtyard"},
                {"label": "NORTH PIER PROMENADE", "x": 110, "y": 16, "w": 460, "h": 28, "kind": "water"},
            ],
            "slots": [
                {"id": "A", "x": 45, "y": 64, "w": 145, "h": 68},
                {"id": "B", "x": 270, "y": 64, "w": 140, "h": 58},
                {"id": "C", "x": 485, "y": 64, "w": 145, "h": 68},
                {"id": "D", "x": 45, "y": 154, "w": 145, "h": 78},
                {"id": "E", "x": 485, "y": 154, "w": 145, "h": 78},
                {"id": "F", "x": 45, "y": 256, "w": 145, "h": 68},
                {"id": "G", "x": 485, "y": 256, "w": 145, "h": 68},
            ],
        },
        "transcript": [
            {"id": "p2-t1", "speaker": "Curator", "style": "welcoming and clear", "text": "Welcome everyone to the newly reopened Harbourview Maritime Museum! Before you explore our galleries, take a quick look at the ground-floor map in your brochure so you can orient yourselves."},
            {"id": "p2-t2", "speaker": "Curator", "style": "informative", "text": "We are standing right now in the Ticket Foyer just inside the South Main Entrance, facing north toward the open Central Courtyard and the North Pier Promenade beyond it."},
            {"id": "p2-t3", "speaker": "Curator", "style": "clear", "text": "First, if you'd like to drop off heavy coats or umbrellas, walk straight to your immediate left from the Ticket Foyer—the southwest room right beside us is the Cloakroom and Lockers, which is completely free today."},
            {"id": "p2-t4", "speaker": "Curator", "style": "clear", "text": "Next, for families heading to our hands-on Navigation Lab, go out into the Central Courtyard and turn west—that's to the left. The middle room along the western wall, directly opposite the courtyard fountain, houses the Navigation Lab with working brass compasses and miniature wind tunnels."},
            {"id": "p2-t5", "speaker": "Curator", "style": "enthusiastic", "text": "Continue north from the Navigation Lab into the northwest corner overlooking the North Pier Promenade, and you'll find our Shipwright's Workshop, where volunteers restore timber dinghies live every afternoon."},
            {"id": "p2-t6", "speaker": "Curator", "style": "clear", "text": "Now, swing across to the eastern wing. Directly opposite the Navigation Lab—in the middle of the east side of the courtyard—sits the Historic Charts Archive. Please note flash photography isn't permitted inside because the seventeenth-century vellum maps are light-sensitive."},
            {"id": "p2-t7", "speaker": "Curator", "style": "warm", "text": "Finally, if you're ready for coffee with a harbour view, head to the northeast corner right next to the North Pier Promenade—that glass-walled corner is our Waterfront Café. We used to keep the café down by the entrance, where the bookshop now sits, so returning visitors often get surprised!"},
            {"id": "p2-t8", "speaker": "Curator", "style": "informative", "text": "Let me also highlight a few updates from our eighteen-month renovation. Many locals assumed we closed solely to fix the leaky Victorian roof, and while we did replace every slate tile, the real driver was installing climate-controlled humidity vaults so we could safely display the salvaged Endeavour timbers on loan from Bristol."},
            {"id": "p2-t9", "speaker": "Curator", "style": "clear", "text": "If you're joining the guided dry-dock tour at two o'clock, there's no extra charge for ticket holders, though spaces are capped at twenty visitors per group, so please pick up a coloured wristband at the foyer desk before one-thirty."},
            {"id": "p2-t10", "speaker": "Curator", "style": "friendly", "text": "Our audio guides have also been redesigned. Instead of punching in exhibit numbers on a keypad, the new handset triggers commentary automatically when you step beside a display—and for younger visitors there's an optional pirate-riddle treasure trail."},
            {"id": "p2-t11", "speaker": "Curator", "style": "helpful", "text": "A quick word about the outdoor historic tugboat moored along the North Pier: boarding is open all afternoon, but wheelchair users should note that the steep wooden gangplank is currently awaiting a hydraulic ramp due next month, so we've installed a live 360-degree deck camera inside the foyer instead."},
            {"id": "p2-t12", "speaker": "Curator", "style": "warm", "text": "Lastly, we're recruiting weekend volunteers for our autumn school programme. You don't need a maritime history degree—full training is provided—we simply ask volunteers to commit to at least two Saturday mornings per month."},
        ],
        "question_groups": [
            {
                "id": "l1-p2-g1",
                "title": "Questions 11–15",
                "question_type": "map_plan_diagram",
                "instructions": "Label the museum floorplan above. Write the correct letter, A–G, next to Questions 11–15.",
                "options": [
                    {"id": "A", "text": "Zone A (Northwest corner)"},
                    {"id": "B", "text": "Zone B (North centre)"},
                    {"id": "C", "text": "Zone C (Northeast corner)"},
                    {"id": "D", "text": "Zone D (West middle)"},
                    {"id": "E", "text": "Zone E (East middle)"},
                    {"id": "F", "text": "Zone F (Southwest beside foyer)"},
                    {"id": "G", "text": "Zone G (Southeast beside foyer)"},
                ],
                "question_numbers": [11, 12, 13, 14, 15],
            },
            {
                "id": "l1-p2-g2",
                "title": "Questions 16–20",
                "question_type": "mcq_single",
                "instructions": "Choose the correct letter, A, B, or C.",
                "question_numbers": [16, 17, 18, 19, 20],
            },
        ],
    },
    {
        "index": 3,
        "title": "Part 3 — Academic Tutorial: Urban Micro-Forests Research",
        "context": "Academic discussion between environmental science students Maya and Liam and their tutor, Dr. Patel.",
        "speakers": [
            {"speaker": "Maya", "voice": "Aoede", "accent": "UK English", "role": "Student"},
            {"speaker": "Liam", "voice": "Fenrir", "accent": "US English", "role": "Student"},
            {"speaker": "Dr. Patel", "voice": "Charon", "accent": "UK English", "role": "Tutor"},
        ],
        "audio_filename": "listening_01_part3.wav",
        "transcript": [
            {"id": "p3-t1", "speaker": "Dr. Patel", "style": "encouraging academic", "text": "Come in, Maya, Liam. Let's review your dissertation pilot on Miyawaki urban micro-forests—those dense tennis-court-sized native woodlands planted in cities."},
            {"id": "p3-t2", "speaker": "Maya", "style": "thoughtful", "text": "Thanks, Dr. Patel. Originally we wanted to measure bird nesting across twelve city plots, but after reading the Utrecht study we realized twelve plots in one semester was way too ambitious—so we narrowed down to four sites and focused on soil moisture and surface cooling instead."},
            {"id": "p3-t3", "speaker": "Liam", "style": "engaged", "text": "Right, and what surprised both of us in the literature review wasn't how fast Miyawaki saplings grow—everyone cites that—it was how heavily survival depends on digging up and amending compacted urban clay beforehand. Skipping soil preparation wiped out nearly half the saplings in the Rotterdam trial."},
            {"id": "p3-t4", "speaker": "Maya", "style": "agreeing", "text": "Definitely. I actually expected drought watering costs to be the biggest failure point, so seeing compacted soil rank higher completely changed our survey checklist."},
            {"id": "p3-t5", "speaker": "Dr. Patel", "style": "analytical", "text": "Good insight. Now, how are you choosing your control sites to compare temperatures against?"},
            {"id": "p3-t6", "speaker": "Liam", "style": "slightly hesitant", "text": "I suggested using a paved school car park right next to each micro-forest, because the temperature contrast would look really dramatic on our graphs."},
            {"id": "p3-t7", "speaker": "Maya", "style": "diplomatic", "text": "Wait—Dr. Patel, wouldn't comparing a forest against black asphalt skew our claim? A conventional mown grass lawn with scattered ornamental trees is a fairer benchmark, since that's what councils actually plant as an alternative."},
            {"id": "p3-t8", "speaker": "Dr. Patel", "style": "approving", "text": "Maya's spot on, Liam. Stick with mown park lawns as your control—examiners immediately spot inflated baselines. Also, be careful with your thermal sensors: mount them inside ventilated white radiation shields rather than bare posts, or direct afternoon sun will corrupt your air-temperature readings."},
            {"id": "p3-t9", "speaker": "Liam", "style": "appreciative", "text": "Great catch, we'll order radiation shields today. What about our community questionnaire? We drafted thirty questions covering biodiversity, shade, and aesthetics."},
            {"id": "p3-t10", "speaker": "Dr. Patel", "style": "practical", "text": "Thirty is far too long for busy park walkers—they'll abandon it halfway. Trim it to ten sharp items and run a quick trial with five classmates first to catch ambiguous wording."},
            {"id": "p3-t11", "speaker": "Maya", "style": "organized", "text": "Makes sense. Let's quickly check our five methodology sections so we know what needs revision before Friday's ethics sign-off. First, our Historical Literature Summary—I thought we might need more Japanese case studies."},
            {"id": "p3-t12", "speaker": "Dr. Patel", "style": "clear", "text": "Actually, your literature summary is already well balanced—no changes needed there."},
            {"id": "p3-t13", "speaker": "Liam", "style": "checking", "text": "Okay, great! What about our Soil Sampling Protocol?"},
            {"id": "p3-t14", "speaker": "Dr. Patel", "style": "precise", "text": "You're taking cores only at ten centimetres deep, which misses deeper root zones—expand it to include thirty-centimetre cores as well."},
            {"id": "p3-t15", "speaker": "Maya", "style": "checking", "text": "Got it—add deeper measurements. Third, the Insect Pitfall Traps section?"},
            {"id": "p3-t16", "speaker": "Dr. Patel", "style": "firm", "text": "Drop the pitfall traps entirely from this pilot; invertebrate identification takes months of lab taxonomy and you'll spread yourselves too thin."},
            {"id": "p3-t17", "speaker": "Liam", "style": "checking", "text": "Fair enough, that saves a huge headache. Fourth, our Resident Interview Script?"},
            {"id": "p3-t18", "speaker": "Dr. Patel", "style": "helpful", "text": "As we just said, shorten it drastically so interviews stay under five minutes."},
            {"id": "p3-t19", "speaker": "Maya", "style": "checking", "text": "And finally, our Statistical Analysis Plan?"},
            {"id": "p3-t20", "speaker": "Dr. Patel", "style": "constructive", "text": "Right now you've listed a simple t-test, which won't handle repeated measurements across four seasons—consult the department statistician to switch to a mixed-effects model."},
        ],
        "question_groups": [
            {
                "id": "l1-p3-g1",
                "title": "Questions 21–25",
                "question_type": "mcq_single",
                "instructions": "Choose the correct letter, A, B, or C.",
                "question_numbers": [21, 22, 23, 24, 25],
            },
            {
                "id": "l1-p3-g2",
                "title": "Questions 26–30",
                "question_type": "matching",
                "instructions": "What action does Dr. Patel recommend for each section of the students' methodology? Choose FIVE answers from the box (A–F) and select the correct letter next to Questions 26–30.",
                "options": [
                    {"id": "A", "text": "Remove this component completely"},
                    {"id": "B", "text": "Reduce its length significantly"},
                    {"id": "C", "text": "Leave it unchanged"},
                    {"id": "D", "text": "Collect data from greater depth"},
                    {"id": "E", "text": "Seek specialist advice to change the analytical method"},
                    {"id": "F", "text": "Translate it into additional local languages"},
                ],
                "question_numbers": [26, 27, 28, 29, 30],
            },
        ],
    },
    {
        "index": 4,
        "title": "Part 4 — Academic Lecture: The Acoustics of Ancient Amphitheatres",
        "context": "University lecture exploring how Greek and Roman architects engineered open-air speech clarity without microphones.",
        "speakers": [
            {"speaker": "Lecturer", "voice": "Charon", "accent": "UK English", "role": "Architectural Acoustics Professor"},
        ],
        "audio_filename": "listening_01_part4.wav",
        "transcript": [
            {"id": "p4-t1", "speaker": "Lecturer", "style": "clear academic lecture", "text": "Today we're examining one of architectural history's most enduring puzzles: how an actor speaking unamplified in the ancient Greek theatre of Epidaurus, built in the fourth century BCE, could be heard distinctly by fourteen thousand spectators sitting sixty metres away."},
            {"id": "p4-t2", "speaker": "Lecturer", "style": "analytical", "text": "For centuries, tour guides credited prevailing hillside breezes or bronze resonating jars hidden beneath the benches. Modern acoustic measurements in 2007 debunked those romantic myths and revealed a far more sophisticated physical mechanism built straight into the carved limestone seating."},
            {"id": "p4-t3", "speaker": "Lecturer", "style": "clear", "text": "First, consider site geometry. Architects carved Epidaurus into a natural hillside with a remarkably steep slope of roughly twenty-six degrees. This sharp incline preserves an unobstructed line of sight—and direct acoustic path—from the circular performance floor, known as the orchestra, all the way to the topmost tier, preventing front-row audiences from absorbing the speaker's voice."},
            {"id": "p4-t4", "speaker": "Lecturer", "style": "informative", "text": "Even more remarkable is how the stepped rows of limestone benches act as a selective acoustic filter. Because the spacing between rows matches the wavelength of low-frequency background noise—such as rustling wind and murmuring crowds below five hundred hertz—the corrugated stone profile cancels out distracting rumble through wave interference."},
            {"id": "p4-t5", "speaker": "Lecturer", "style": "engaging", "text": "Meanwhile, higher frequencies essential for recognizing spoken consonants bounce cleanly off the dense limestone risers toward listeners' ears. Interestingly, the human auditory brain automatically fills in the suppressed fundamental bass tones of a speaker's voice—a psychoacoustic effect called virtual pitch—so speech still sounds warm and natural rather than tinny."},
            {"id": "p4-t6", "speaker": "Lecturer", "style": "clear", "text": "Now, what happened when Roman engineers adapted Greek designs into freestanding urban amphitheatres? Unlike Greek builders who relied on rural hillsides, Romans used vaulted concrete arches to erect theatres inside flat, noisy city centres. To block street chatter and reflect vocal energy back toward audiences, they raised a tall decorated backdrop wall behind the stage called the scaenae frons."},
            {"id": "p4-t7", "speaker": "Lecturer", "style": "analytical", "text": "Roman builders also stretched retractable canvas awnings—velaria—overhead to shield crowds from Mediterranean sun. While welcome for thermal comfort, acoustic simulations show those heavy fabric canopies subtly dampened upper-tier reverberation, trading slight brilliance for cooler seating."},
            {"id": "p4-t8", "speaker": "Lecturer", "style": "concluding", "text": "Contemporary auditorium designers still borrow these two-thousand-year-old principles. When renovating outdoor concert shells or university lecture halls, engineers tune stair-stepped diffusers to suppress low-frequency ventilation hum without relying on costly electronic equalizers—proving that stone geometry remains one of our purest acoustic instruments."},
        ],
        "question_groups": [
            {
                "id": "l1-p4-g1",
                "title": "Questions 31–40",
                "question_type": "form_note_table_completion",
                "instructions": "Complete the lecture notes below. Write ONE WORD ONLY for each answer.",
                "word_limit": {
                    "max_words": 1,
                    "allow_number": False,
                    "label": "ONE WORD ONLY",
                },
                "note_heading": "Acoustics of Ancient Greek & Roman Theatres",
                "question_numbers": [31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
            }
        ],
    },
]

LISTENING_QUESTIONS: list[dict[str, Any]] = [
    # ==================== PART 1 (Q1-Q10) ====================
    {
        "id": "l1-q01",
        "passage_index": 1,
        "question_number": 1,
        "question_type": "form_note_table_completion",
        "target_band": 5.5,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Applicant's surname: David ________",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["Hargreaves"]},
        "evidence_span": {
            "transcript_id": "p1-t4",
            "quote": "Sure, it's David Hargreaves. That's spelled H-A-R-G-R-E-A-V-E-S.",
            "distractor_note": "Spelled aloud letter-by-letter; watch exact spelling of Hargreaves.",
        },
    },
    {
        "id": "l1-q02",
        "passage_index": 1,
        "question_number": 2,
        "question_type": "form_note_table_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Postcode for mailing boathouse pass: ________",
            "word_limit": {"max_words": 2, "allow_number": True, "label": "POSTCODE / CODE"},
        },
        "answer_key": {"accepted": ["BH14 7QR"], "is_code": True},
        "evidence_span": {
            "transcript_id": "p1-t6",
            "quote": "oh yes, it's BH14 7QR.",
            "distractor_note": "UK alphanumeric postcode; both 'BH14 7QR' and 'BH147QR' are accepted.",
        },
    },
    {
        "id": "l1-q03",
        "passage_index": 1,
        "question_number": 3,
        "question_type": "form_note_table_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Selected six-week starter pass fee: £________",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["£45", "45"]},
        "evidence_span": {
            "transcript_id": "p1-t7",
            "quote": "standard annual fee used to be 140 pounds... now 165 pounds—or you can try a six-week starter pass for 45 pounds.",
            "distractor_note": "Classic price distractor: £140 (old annual) and £165 (new annual) are mentioned before David selects the £45 starter pass.",
        },
    },
    {
        "id": "l1-q04",
        "passage_index": 1,
        "question_number": 4,
        "question_type": "form_note_table_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Rescheduled safety induction date: ________ July",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["14", "14th", "14 July", "14th July"]},
        "evidence_span": {
            "transcript_id": "p1-t9",
            "quote": "We normally run those on Thursday mornings, oh wait—our slipway is being resurfaced this Thursday, so this week's induction has moved to Saturday the 14th of July.",
            "distractor_note": "Self-correction trap: 'Thursday' is cancelled due to slipway resurfacing; the actual date is 14 / 14th.",
        },
    },
    {
        "id": "l1-q05",
        "passage_index": 1,
        "question_number": 5,
        "question_type": "form_note_table_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Required arrival time for lifejacket fitting: ________",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["9:30", "9:30 am", "9.30", "9.30 am"]},
        "evidence_span": {
            "transcript_id": "p1-t11",
            "quote": "Water launch is at ten o'clock sharp, so please arrive by 9:30 am for your lifejacket fitting and briefing.",
            "distractor_note": "10:00 is the water launch distractor; required arrival time is 9:30 / 9:30 am.",
        },
    },
    {
        "id": "l1-q06",
        "passage_index": 1,
        "question_number": 6,
        "question_type": "form_note_table_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Recommended footwear: old waterproof ________ (or neoprene booties)",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["sandals"]},
        "evidence_span": {
            "transcript_id": "p1-t13",
            "quote": "bring old waterproof sandals or neoprene booties, plus a reusable bottle of water and strong sunscreen.",
            "distractor_note": "Plural noun 'sandals' is required ('sandal' singular loses the mark).",
        },
    },
    {
        "id": "l1-q07",
        "passage_index": 1,
        "question_number": 7,
        "question_type": "form_note_table_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Additional personal item to bring with water bottle: strong ________",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["sunscreen"]},
        "evidence_span": {
            "transcript_id": "p1-t13",
            "quote": "plus a reusable bottle of water and strong sunscreen.",
            "distractor_note": "Exact single word following 'strong'.",
        },
    },
    {
        "id": "l1-q08",
        "passage_index": 1,
        "question_number": 8,
        "question_type": "form_note_table_completion",
        "target_band": 6.0,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Applicant's prior water-sport experience: ________",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["kayaking"]},
        "evidence_span": {
            "transcript_id": "p1-t14",
            "quote": "Should I mention that I did a little kayaking at university",
            "distractor_note": "Exact activity noun 'kayaking'.",
        },
    },
    {
        "id": "l1-q09",
        "passage_index": 1,
        "question_number": 9,
        "question_type": "form_note_table_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Free member parking is located behind the old ________ on Marina Lane.",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["bakery"]},
        "evidence_span": {
            "transcript_id": "p1-t17",
            "quote": "members get two hours of free parking behind the old bakery.",
            "distractor_note": "The pier car park and lighthouse are navigation distractors; free parking is behind the old 'bakery'.",
        },
    },
    {
        "id": "l1-q10",
        "passage_index": 1,
        "question_number": 10,
        "question_type": "form_note_table_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p1-g1",
            "prompt": "Contact person if arriving early: Coach ________",
            "word_limit": {"max_words": 1, "allow_number": True, "label": "ONE WORD AND/OR A NUMBER"},
        },
        "answer_key": {"accepted": ["Martin"]},
        "evidence_span": {
            "transcript_id": "p1-t19",
            "quote": "ask for Coach Martin if you arrive early.",
            "distractor_note": "Don't confuse Claire (the receptionist) with Coach Martin.",
        },
    },
    # ==================== PART 2 (Q11-Q15 Map Labelling, Q16-Q20 MCQ) ====================
    {
        "id": "l1-q11",
        "passage_index": 2,
        "question_number": 11,
        "question_type": "map_plan_diagram",
        "target_band": 6.0,
        "prompt_payload": {"group_id": "l1-p2-g1", "prompt": "Cloakroom and Lockers"},
        "answer_key": {"accepted": ["F"]},
        "evidence_span": {
            "transcript_id": "p2-t3",
            "quote": "walk straight to your immediate left from the Ticket Foyer—the southwest room right beside us is the Cloakroom and Lockers",
            "distractor_note": "Facing north from Ticket Foyer, immediate left (southwest) is Zone F.",
        },
    },
    {
        "id": "l1-q12",
        "passage_index": 2,
        "question_number": 12,
        "question_type": "map_plan_diagram",
        "target_band": 6.5,
        "prompt_payload": {"group_id": "l1-p2-g1", "prompt": "Navigation Lab"},
        "answer_key": {"accepted": ["D"]},
        "evidence_span": {
            "transcript_id": "p2-t4",
            "quote": "The middle room along the western wall, directly opposite the courtyard fountain, houses the Navigation Lab",
            "distractor_note": "Middle of the western wall facing the Central Courtyard is Zone D.",
        },
    },
    {
        "id": "l1-q13",
        "passage_index": 2,
        "question_number": 13,
        "question_type": "map_plan_diagram",
        "target_band": 6.5,
        "prompt_payload": {"group_id": "l1-p2-g1", "prompt": "Shipwright's Workshop"},
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "transcript_id": "p2-t5",
            "quote": "Continue north from the Navigation Lab into the northwest corner overlooking the North Pier Promenade, and you'll find our Shipwright's Workshop",
            "distractor_note": "Northwest corner above Zone D is Zone A.",
        },
    },
    {
        "id": "l1-q14",
        "passage_index": 2,
        "question_number": 14,
        "question_type": "map_plan_diagram",
        "target_band": 6.5,
        "prompt_payload": {"group_id": "l1-p2-g1", "prompt": "Historic Charts Archive"},
        "answer_key": {"accepted": ["E"]},
        "evidence_span": {
            "transcript_id": "p2-t6",
            "quote": "Directly opposite the Navigation Lab—in the middle of the east side of the courtyard—sits the Historic Charts Archive.",
            "distractor_note": "Directly across the courtyard from Zone D on the east wall is Zone E.",
        },
    },
    {
        "id": "l1-q15",
        "passage_index": 2,
        "question_number": 15,
        "question_type": "map_plan_diagram",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "l1-p2-g1", "prompt": "Waterfront Café"},
        "answer_key": {"accepted": ["C"]},
        "evidence_span": {
            "transcript_id": "p2-t7",
            "quote": "head to the northeast corner right next to the North Pier Promenade—that glass-walled corner is our Waterfront Café. We used to keep the café down by the entrance",
            "distractor_note": "Past-location distractor! It USED to be near the entrance (G), but is now in the northeast corner (C).",
        },
    },
    {
        "id": "l1-q16",
        "passage_index": 2,
        "question_number": 16,
        "question_type": "mcq_single",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p2-g2",
            "prompt": "What was the main reason the museum closed for an eighteen-month renovation?",
            "options": [
                {"id": "A", "text": "To repair damaged Victorian roof slates"},
                {"id": "B", "text": "To build climate-controlled storage for borrowed ship timbers"},
                {"id": "C", "text": "To enlarge the waterfront bookshop"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p2-t8",
            "quote": "while we did replace every slate tile, the real driver was installing climate-controlled humidity vaults so we could safely display the salvaged Endeavour timbers on loan from Bristol.",
            "distractor_note": "Option A was a secondary repair; 'the real driver' points directly to B.",
        },
    },
    {
        "id": "l1-q17",
        "passage_index": 2,
        "question_number": 17,
        "question_type": "mcq_single",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p2-g2",
            "prompt": "What must visitors do to join the two o'clock dry-dock tour?",
            "options": [
                {"id": "A", "text": "Pay a small supplementary fee at the dock"},
                {"id": "B", "text": "Collect a wristband from the foyer desk before 1:30"},
                {"id": "C", "text": "Reserve a place online at least one day ahead"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p2-t9",
            "quote": "there's no extra charge for ticket holders, though spaces are capped at twenty visitors per group, so please pick up a coloured wristband at the foyer desk before one-thirty.",
            "distractor_note": "'no extra charge' eliminates A; collecting a wristband confirms B.",
        },
    },
    {
        "id": "l1-q18",
        "passage_index": 2,
        "question_number": 18,
        "question_type": "mcq_single",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p2-g2",
            "prompt": "What is new about the redesigned museum audio guides?",
            "options": [
                {"id": "A", "text": "They start playing automatically when visitors stand near an exhibit"},
                {"id": "B", "text": "Visitors enter shorter two-digit codes on a keypad"},
                {"id": "C", "text": "They are available exclusively for children's groups"},
            ],
        },
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "transcript_id": "p2-t10",
            "quote": "Instead of punching in exhibit numbers on a keypad, the new handset triggers commentary automatically when you step beside a display",
            "distractor_note": "Keypad entry is explicitly contrasted as the OLD system.",
        },
    },
    {
        "id": "l1-q19",
        "passage_index": 2,
        "question_number": 19,
        "question_type": "mcq_single",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p2-g2",
            "prompt": "How is the museum currently accommodating wheelchair users for the historic tugboat?",
            "options": [
                {"id": "A", "text": "A hydraulic ramp has already been fitted to the gangplank"},
                {"id": "B", "text": "A live 360-degree camera feed is available in the foyer"},
                {"id": "C", "text": "The tugboat is temporarily closed to all visitors"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p2-t11",
            "quote": "the steep wooden gangplank is currently awaiting a hydraulic ramp due next month, so we've installed a live 360-degree deck camera inside the foyer instead.",
            "distractor_note": "Tense trap: the hydraulic ramp (A) is NOT installed yet ('due next month').",
        },
    },
    {
        "id": "l1-q20",
        "passage_index": 2,
        "question_number": 20,
        "question_type": "mcq_single",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p2-g2",
            "prompt": "What is required of applicants for the autumn weekend volunteer programme?",
            "options": [
                {"id": "A", "text": "A university qualification in maritime history"},
                {"id": "B", "text": "Previous experience teaching primary school groups"},
                {"id": "C", "text": "Availability for at least two Saturday mornings each month"},
            ],
        },
        "answer_key": {"accepted": ["C"]},
        "evidence_span": {
            "transcript_id": "p2-t12",
            "quote": "You don't need a maritime history degree—full training is provided—we simply ask volunteers to commit to at least two Saturday mornings per month.",
            "distractor_note": "History degree (A) is explicitly ruled out.",
        },
    },
    # ==================== PART 3 (Q21-Q25 MCQ, Q26-Q30 Matching) ====================
    {
        "id": "l1-q21",
        "passage_index": 3,
        "question_number": 21,
        "question_type": "mcq_single",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p3-g1",
            "prompt": "Why did Maya and Liam narrow their micro-forest study from twelve sites to four?",
            "options": [
                {"id": "A", "text": "The Utrecht study proved bird surveys were scientifically invalid"},
                {"id": "B", "text": "Covering twelve sites within a single semester was unrealistic"},
                {"id": "C", "text": "City councils refused permission for eight of the plots"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p3-t2",
            "quote": "after reading the Utrecht study we realized twelve plots in one semester was way too ambitious—so we narrowed down to four sites",
            "distractor_note": "'way too ambitious' paraphrases 'unrealistic' (B).",
        },
    },
    {
        "id": "l1-q22",
        "passage_index": 3,
        "question_number": 22,
        "question_type": "mcq_single",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p3-g1",
            "prompt": "What surprised BOTH students in the literature review?",
            "options": [
                {"id": "A", "text": "How quickly Miyawaki saplings grow in dense clusters"},
                {"id": "B", "text": "How strongly sapling survival depends on preparing compacted soil"},
                {"id": "C", "text": "How expensive summer drought watering can become"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p3-t3",
            "quote": "what surprised both of us in the literature review wasn't how fast Miyawaki saplings grow—everyone cites that—it was how heavily survival depends on digging up and amending compacted urban clay beforehand.",
            "distractor_note": "Both A ('everyone cites that') and C (Maya's prior expectation) are distractors.",
        },
    },
    {
        "id": "l1-q23",
        "passage_index": 3,
        "question_number": 23,
        "question_type": "mcq_single",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p3-g1",
            "prompt": "Which control site do they finally agree to use for temperature comparisons?",
            "options": [
                {"id": "A", "text": "A paved school car park"},
                {"id": "B", "text": "A conventional mown grass park lawn"},
                {"id": "C", "text": "An unshaded rooftop garden"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p3-t8",
            "quote": "Maya's spot on, Liam. Stick with mown park lawns as your control—examiners immediately spot inflated baselines.",
            "distractor_note": "Liam initially proposed a car park (A), but Maya and Dr. Patel reject it in favour of mown park lawns (B).",
        },
    },
    {
        "id": "l1-q24",
        "passage_index": 3,
        "question_number": 24,
        "question_type": "mcq_single",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "l1-p3-g1",
            "prompt": "Why does Dr. Patel advise placing thermal sensors inside white radiation shields?",
            "options": [
                {"id": "A", "text": "To stop direct sunlight from skewing air-temperature data"},
                {"id": "B", "text": "To protect wiring from park lawnmowers"},
                {"id": "C", "text": "To disguise equipment from curious passersby"},
            ],
        },
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "transcript_id": "p3-t8",
            "quote": "mount them inside ventilated white radiation shields rather than bare posts, or direct afternoon sun will corrupt your air-temperature readings.",
            "distractor_note": "Direct reason is avoiding sun-corrupted readings (A).",
        },
    },
    {
        "id": "l1-q25",
        "passage_index": 3,
        "question_number": 25,
        "question_type": "mcq_single",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "l1-p3-g1",
            "prompt": "What does Dr. Patel recommend before using the shortened questionnaire in parks?",
            "options": [
                {"id": "A", "text": "Post it on a municipal social-media page"},
                {"id": "B", "text": "Test it with a small group of fellow students"},
                {"id": "C", "text": "Have the city council approve the biodiversity questions"},
            ],
        },
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p3-t10",
            "quote": "Trim it to ten sharp items and run a quick trial with five classmates first to catch ambiguous wording.",
            "distractor_note": "'run a quick trial with five classmates' paraphrases B.",
        },
    },
    {
        "id": "l1-q26",
        "passage_index": 3,
        "question_number": 26,
        "question_type": "matching",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "l1-p3-g2", "prompt": "Historical Literature Summary"},
        "answer_key": {"accepted": ["C"]},
        "evidence_span": {
            "transcript_id": "p3-t12",
            "quote": "Actually, your literature summary is already well balanced—no changes needed there.",
            "distractor_note": "Maya suspects it needs more Japanese studies, but Dr. Patel says 'no changes needed' (C).",
        },
    },
    {
        "id": "l1-q27",
        "passage_index": 3,
        "question_number": 27,
        "question_type": "matching",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "l1-p3-g2", "prompt": "Soil Sampling Protocol"},
        "answer_key": {"accepted": ["D"]},
        "evidence_span": {
            "transcript_id": "p3-t14",
            "quote": "You're taking cores only at ten centimetres deep, which misses deeper root zones—expand it to include thirty-centimetre cores as well.",
            "distractor_note": "Expanding from 10 cm to 30 cm cores matches D ('Collect data from greater depth').",
        },
    },
    {
        "id": "l1-q28",
        "passage_index": 3,
        "question_number": 28,
        "question_type": "matching",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "l1-p3-g2", "prompt": "Insect Pitfall Traps"},
        "answer_key": {"accepted": ["A"]},
        "evidence_span": {
            "transcript_id": "p3-t16",
            "quote": "Drop the pitfall traps entirely from this pilot",
            "distractor_note": "'Drop... entirely' matches A ('Remove this component completely').",
        },
    },
    {
        "id": "l1-q29",
        "passage_index": 3,
        "question_number": 29,
        "question_type": "matching",
        "target_band": 7.0,
        "prompt_payload": {"group_id": "l1-p3-g2", "prompt": "Resident Interview Script"},
        "answer_key": {"accepted": ["B"]},
        "evidence_span": {
            "transcript_id": "p3-t18",
            "quote": "shorten it drastically so interviews stay under five minutes.",
            "distractor_note": "'shorten it drastically' matches B ('Reduce its length significantly').",
        },
    },
    {
        "id": "l1-q30",
        "passage_index": 3,
        "question_number": 30,
        "question_type": "matching",
        "target_band": 7.5,
        "prompt_payload": {"group_id": "l1-p3-g2", "prompt": "Statistical Analysis Plan"},
        "answer_key": {"accepted": ["E"]},
        "evidence_span": {
            "transcript_id": "p3-t20",
            "quote": "consult the department statistician to switch to a mixed-effects model.",
            "distractor_note": "'consult the department statistician' matches E ('Seek specialist advice to change the analytical method').",
        },
    },
    # ==================== PART 4 (Q31-Q40 Lecture Note Completion, ONE WORD ONLY) ====================
    {
        "id": "l1-q31",
        "passage_index": 4,
        "question_number": 31,
        "question_type": "form_note_table_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Early tour guides wrongly attributed clarity to hillside winds or hidden ________ jars.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["bronze"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t2",
            "quote": "tour guides credited prevailing hillside breezes or bronze resonating jars hidden beneath the benches.",
            "distractor_note": "Material adjective 'bronze' fits ONE WORD ONLY.",
        },
    },
    {
        "id": "l1-q32",
        "passage_index": 4,
        "question_number": 32,
        "question_type": "form_note_table_completion",
        "target_band": 6.5,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "A steep seating ________ of 26 degrees kept a clear acoustic path from stage to top row.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["slope", "incline"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t3",
            "quote": "carved Epidaurus into a natural hillside with a remarkably steep slope of roughly twenty-six degrees.",
            "distractor_note": "Exact noun 'slope' (or 'incline').",
        },
    },
    {
        "id": "l1-q33",
        "passage_index": 4,
        "question_number": 33,
        "question_type": "form_note_table_completion",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "The circular performance floor at the base was known as the ________.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["orchestra"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t3",
            "quote": "from the circular performance floor, known as the orchestra",
            "distractor_note": "Exact architectural term 'orchestra'.",
        },
    },
    {
        "id": "l1-q34",
        "passage_index": 4,
        "question_number": 34,
        "question_type": "form_note_table_completion",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Carved rows of ________ seating functioned as a selective acoustic filter.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["limestone"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t4",
            "quote": "the stepped rows of limestone benches act as a selective acoustic filter.",
            "distractor_note": "Exact stone material 'limestone'.",
        },
    },
    {
        "id": "l1-q35",
        "passage_index": 4,
        "question_number": 35,
        "question_type": "form_note_table_completion",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Low-frequency wind and crowd rumble was suppressed through wave ________.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["interference"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t4",
            "quote": "cancels out distracting rumble through wave interference.",
            "distractor_note": "Exact physics noun after 'wave'.",
        },
    },
    {
        "id": "l1-q36",
        "passage_index": 4,
        "question_number": 36,
        "question_type": "form_note_table_completion",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Higher frequencies crucial for hearing spoken ________ reflected clearly to the audience.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["consonants"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t5",
            "quote": "higher frequencies essential for recognizing spoken consonants bounce cleanly off the dense limestone risers",
            "distractor_note": "Plural noun 'consonants' is required.",
        },
    },
    {
        "id": "l1-q37",
        "passage_index": 4,
        "question_number": 37,
        "question_type": "form_note_table_completion",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "The brain reconstructs missing bass frequencies via a phenomenon called virtual ________.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["pitch"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t5",
            "quote": "a psychoacoustic effect called virtual pitch",
            "distractor_note": "Exact single word following 'virtual'.",
        },
    },
    {
        "id": "l1-q38",
        "passage_index": 4,
        "question_number": 38,
        "question_type": "form_note_table_completion",
        "target_band": 7.0,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Roman architects built freestanding urban theatres using vaulted ________ arches.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["concrete"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t6",
            "quote": "Romans used vaulted concrete arches to erect theatres inside flat, noisy city centres.",
            "distractor_note": "Exact material word 'concrete'.",
        },
    },
    {
        "id": "l1-q39",
        "passage_index": 4,
        "question_number": 39,
        "question_type": "form_note_table_completion",
        "target_band": 7.5,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Overhead ________ awnings shaded Roman audiences while slightly softening upper-tier acoustics.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["canvas"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t7",
            "quote": "Roman builders also stretched retractable canvas awnings—velaria—overhead",
            "distractor_note": "Exact material noun before 'awnings'.",
        },
    },
    {
        "id": "l1-q40",
        "passage_index": 4,
        "question_number": 40,
        "question_type": "form_note_table_completion",
        "target_band": 8.0,
        "prompt_payload": {
            "group_id": "l1-p4-g1",
            "prompt": "Modern lecture halls still use stepped diffusers to reduce low-frequency ________ hum.",
            "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"},
        },
        "answer_key": {"accepted": ["ventilation"], "word_limit": {"max_words": 1, "allow_number": False, "label": "ONE WORD ONLY"}},
        "evidence_span": {
            "transcript_id": "p4-t8",
            "quote": "engineers tune stair-stepped diffusers to suppress low-frequency ventilation hum",
            "distractor_note": "Exact modifier before 'hum'.",
        },
    },
]


def seed_listening_mock(db: Session) -> bool:
    """Seed the original 4-part, 40-question Academic Listening mock test idempotently."""
    existing = db.get(ListeningTest, LISTENING_TEST_ID)
    if existing is not None:
        return False

    test = ListeningTest(
        id=LISTENING_TEST_ID,
        title="IELTS Academic Listening Practice Test 01",
        subtitle=(
            "Official post-2020 4-Part format (40 questions, 30 min): Rowing Club Enquiry, "
            "Maritime Museum Floorplan Map, Urban Micro-Forests Tutorial, and Ancient Amphitheatre Acoustics."
        ),
        difficulty_label="Band 6.0–8.5",
        duration_minutes=30,
        parts_json=LISTENING_PARTS,
        verified=True,
    )
    db.add(test)

    for q in LISTENING_QUESTIONS:
        db.add(
            QuestionItem(
                id=q["id"],
                listening_test_id=LISTENING_TEST_ID,
                passage_index=q["passage_index"],
                question_number=q["question_number"],
                module="listening",
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
