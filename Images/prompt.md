# Image Generation Prompts

This document contains templates for generating or re-generating artwork for the various Book adaptations of *The Keepers of Mordrin*. These prompts are designed to ensure artistic consistency across all generated images, regardless of whether the source material is a top-down battlemap or a scenic "flavor" image.

# Picturebooks

## Base Prompt: Art Style
Tested Prompt (works well): Watercolor painting style with soft, translucent washes and visible brushstrokes creating gentle textures; delicate, flowing linework defines forms without harsh outlines; warm earthy tones dominate—greens, browns, ochres—with bright accents of gold, pink, and orange; overall aesthetic is whimsical, luminous, and painterly, evoking hand-drawn fantasy illustration with an airy atmosphere.

Was: The art style of the output image is watercolor with overlapping colors, soft edges, and with cute, friendly characters from a childrens book. The image is relatively simple, avoiding complex details and instead relying on rich colors to convey whimsy. Characters are painted with lanky proportions and stylized facial features.

## Base Prompt: Character
Retain the character's defining facial features. She has white hair, pointed ears, and green eyes.

* **ERYNETH**: Retain the character's defining facial features. She has white hair, pointed ears, and green eyes. She is wearing leather armor, brown pants, and a blue cloak. She has green pads on her shoulders and hips. She has a quiver of white-feathered arrows on her back. She has a wooden longbow behind her back.

* **CARYNDAL**: Retain the character's defining facial features. He has brown hair, pointed ears, and blue eyes. He is wearing a green tunic, green pants, and a brown cloak. He has golden armor on his shoulders. He has a large black shield with a golden bird symbol inlaid on its surface.

* **AKNEMEIA**: Retain the character's defining facial features. She has red hair, pointed ears, black horns, gold eyes, and her skin is flecked with golden dragon scales. She is wearing a pink dress, a black scaled cloak, and brown boots.

* **SZETH**: Retain the character's defining facial features. He is young, bald, nimble, and slender. He is wearing a simple white robe and simple white cloak with a tall collar and a brown belt. He is wearing brown sandals. He is holding a long spear with a wooden handle. The spear has magical writing on it.

# Chapterbooks

## Base Prompt: Interior Art Style (Black & White Vignettes)
Clean black-and-white digital pen-and-ink vignette illustration for a children's high-fantasy chapterbook. Bold, crisp black outer contour lines with finer interior linework and clean parallel line hatching for wood grain, stone, and foliage textures. High contrast with selective solid black ink fills for deep shadows or dark magic, and minimal, subtle grayscale shading. Unbordered frameless vignette composition that fades naturally into a pure, solid stark white (#FFFFFF) background around the outer edges. Landscape orientation (3:2 or 4:3 aspect ratio). No rectangular border, no frame, no color, no messy pencil sketch lines, no paper texture.

## Base Prompt: Chapterbook Characters (Monochrome Line Art)
When including characters in Chapterbook scenes, render them with clean, approachable, slightly stylized youth-fantasy proportions, expressive eyes, and smooth unhatched skin on their faces:

* **AKNEMEIA**: Young female tiefling sorceress with two curved solid-black horns rising from her forehead, pointed elf-like ears, and long straight light-toned hair with bangs. She wears a belted fantasy tunic/dress and a cloak studded with dark dragonscales along the shoulders.
* **SZETH**: Young bald human warrior-monk with a clean-shaven face, nimble build, wearing a simple white martial arts wrap robe (gi) tied with a dark sash belt and sandals. He carries a rune-carved shortsword (*Istamlakh*) or greatsword (*Beastslayer*).
* **ERYNETH**: Young female elf ranger with pointed ears and light/white hair tied back in a high ponytail with bangs. She wears **fitted dark-shaded leather armor (cuirass/vest), trousers, and boots (never a robe or dress)**, arm bracers, a quiver of arrows, and a wooden longbow.
* **CARYNDAL**: Male half-elf with pointed ears, short solid-black hair, and a neatly trimmed dark beard, wearing fantasy shoulder armor (pauldrons), breastplate, and bracers, and carrying a lute.

## Subject Selection & Composition Guidelines (AI-Aware Best Practices)
To maximize visual consistency across books and minimize AI generation artifacts (such as shifting facial features, mismatched outfits, or tangled multi-character poses), select and compose Chapterbook illustrations according to the following hierarchy:

1. **Prefer Evocative Single-Item or Close-Up Spot Vignettes (Highest Priority):**
   - Whenever a scene can be represented by an iconic object, symbol, or tight close-up action, choose that over a full group scene (e.g., *a close-up of a single hand scorching a raven emblem onto parchment beside a jar of pickled eggs*, *a sword driven into turf*, *a shattered staff and crystal*, or *three ancient dwarven tomes on a stone pedestal*).
2. **Use Simple, Uncluttered Scene Layouts & Environments:**
   - Keep compositions simple with **one clear focal point** and at most 1–2 supporting elements.
   - Frequently use unpopulated or lightly populated environmental vignettes (e.g., *a sunken halfling inn*, *a torchlit dungeon corridor*, *a grand banquet table*, or *kobolds peeking from behind cavern rocks*) where character-to-character continuity is not required.
3. **Pull the Camera Back (Wide Shots & Rear/Three-Quarter Silhouettes):**
   - When characters or combat *are* shown, use a **slightly further-off (wide or medium-wide) camera angle** and frame characters **from behind, over the shoulder, or at a small scale** facing a large monster or landmark (as in `01_TKoM_01.1`, `07.1`, `08.1`, and `09.1`). This makes small facial and costume details much less important.
4. **Limit Multi-Character Close-Ups & Complex Interactions:**
   - Avoid medium/close-up shots of all four protagonists together unless essential. If a character-focused vignette is needed, feature **at most 1–2 characters** in a simple, readable pose (as in `01_TKoM_05.2` or `06.1`).
   - Do not prompt four distinct characters simultaneously performing four different weapon/spell actions in the same frame.
5. **Avoid In-Image Text:**
   - Do not prompt for readable signs, banners, or book titles inside interior vignettes; rely on visual icons instead (e.g., a painted egg sign rather than the words *"The Pickled Egg"*).

## Chapterbook Vignette Templates (Ordered by Preference)

### 1. Iconic Object / Close-Up Spot Vignette (Preferred)
> "[Insert Base Interior Art Style]. A centered, uncluttered spot illustration of [describe a single evocative object or tight close-up action, e.g., a single hand with a tiny spark of fire at the fingertip scorching a bold raven silhouette onto a square of parchment, resting on a wooden bar counter beside a glass jar of pickled eggs]. Simple composition with minimal surrounding lines and generous pure white (#FFFFFF) negative space."

### 2. Simple Environmental / Creature Vignette (Preferred)
> "[Insert Base Interior Art Style]. A clean, simple view of [describe a single location or creature focus, e.g., a towering swirling water monster rising up from a murky swamp lake framed by willow trees / a crooked halfling tavern partially sunken into a dirt sinkhole]. Uncluttered layout with a single clear focal point, tapering off cleanly into a pure white (#FFFFFF) background."

### 3. Pulled-Back / Wide-Angle Action Vignette (Use Sparingly)
> "[Insert Base Interior Art Style]. A wide, pulled-back shot of [describe large landmark or monster in the center, e.g., a massive burrowing landshark erupting from the dirt in a ruined mining town], with [1–2 small or rear-facing adventurer silhouettes in the foreground/distance] for scale. Camera is positioned far enough back that fine facial and outfit details are simplified. Framing elements fade naturally into the pure white (#FFFFFF) background."

## Base Prompt: Chapterbook Cover Art
> "A bold, painterly dark-fantasy book cover illustration in portrait orientation (3:4 aspect ratio). Centered heraldic emblem composition featuring [central motif, e.g., a fierce silver dragon and a shadowy black dragon locked in a spiral / a stylized black raven with outstretched wings] set in front of an ornate, symmetrical golden Celtic/arcane geometric crest. Swirling ribbons of deep obsidian-black shadow smoke curl around the emblem against a [textured parchment / pitch-black] background. Classic embossed metallic gold serif typography at the top reading '[TOP TITLE]' and at the bottom reading '[BOTTOM TITLE]'."

# Adult Novel / Campaign Concept Art (Digital Painting)
*   **Art Style:** High fantasy, digital painting style (similar to official D&D 5e sourcebooks or Magic: The Gathering card art).
*   **Lighting:** Dramatic and cinematic. Strong use of chiaroscuro (contrast between light and dark) to emphasize the campaign's core themes of Selune (light) vs. Shar (shadow).
*   **Color Palette:** Rich, saturated colors. Ethereal blue, green, and silver for scenes involving Selune or fey magic; deep purple and obsidian black for scenes involving Shar, the Shadowfell, or the Underdark.


## Template 1: Adapting a Battlemap into a Scenic Splash

Use this template when converting a top-down tactical battlemap into a dynamic, in-world perspective image.

**Instructions:** Describe the key elements of the map (terrain, structural details, lighting sources) and shift the perspective to a ground-level or slightly elevated cinematic angle. Do *not* include grid lines or UI elements.

**Prompt Template:**
> "A cinematic, digital fantasy illustration of [Describe the location, e.g., a ruined dwarven temple deep underground]. The camera angle is [e.g., ground-level, looking up at a massive statue / a sweeping wide shot of the cavern]. The scene features [List 2-3 key visual elements from the map, e.g., glowing mushroom clusters, a crumbling stone bridge over a chasm, ancient geometric pillars]. The lighting is [Describe the lighting, e.g., dim and eerie, illuminated only by bioluminescence and a single shaft of moonlight]. The style is high-fantasy digital painting, highly detailed, atmospheric, with a focus on environmental storytelling, similar to official Dungeons & Dragons concept art. No grid lines, no UI, purely scenic."

---

## Template 2: Enhancing a "Flavor" Image 

Use this template when taking an existing scenic image or character portrait and ensuring it matches the project's consistent art style. If using an image-to-image AI tool, use the original image as the base.

**Instructions:** Describe the contents of the original image accurately, but enforce the strict stylistic keywords required for this project to unify the look.

**Prompt Template:**
> "A breathtaking, high-fantasy digital painting of [Describe the core subject, e.g., a massive silver dragon roaring at the sky / a bustling pirate port at sunset]. The scene showcases [List key details, e.g., ships with tattered sails, a looming volcanic peak in the background]. The atmosphere is [e.g., tense, majestic, sorrowful]. Lighting is incredibly cinematic and dramatic, emphasizing [e.g., striking silver moonlight piercing through dark storm clouds]. Painted in a polished, highly detailed fantasy concept art style, masterpiece quality, evoking the epic scale of a D&D campaign."

---

## Format-Specific Considerations

Depending on which book the image is being generated for, you may need to add these modifiers to the end of the prompt:

*   **For the Picturebook:** Add: *"The composition should be simple and clear, with bold shapes, slightly softer/friendlier features suitable for children, but retaining the epic fantasy feel. Leave negative space at the [top/bottom/side] for text."*
*   **For the Young Adult Book:** Add: *"The mood should be adventurous and dynamic, focusing on wonder and excitement without overly graphic or terrifying elements."*
*   **For the Novel (Appendix/Inserts):** Add: *"The tone should be gritty, mature, and deeply atmospheric, fully embracing the dark and complex themes of the lore."*
