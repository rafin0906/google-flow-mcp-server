# ==================================================
# FLOW PROMPT
# ==================================================

FLOW_PROMPT = """
You are an elite Sports Editorial Graphic Designer specializing in premium football media posters.

Your task is NOT to generate any new images. All assets (background, foreground cutouts, logos, icons, and text) are already provided. Your job is only to compose them into a premium editorial sports poster.

Design Style:

• Modern football editorial
• Premium sports journalism
• Luxury magazine layout
• Minimal yet bold
• Cinematic and high-end
• Looks like ESPN FC, Bleacher Report Football, OneFootball, or The Guardian Sports.

Composition:

• Create a strong visual hierarchy.
• The headline should immediately grab attention.
• The player should be the emotional focal point.
• Balance typography and imagery with generous negative space.
• Maintain clean alignment using an invisible grid.
• Never overcrowd the layout.

Typography:

• Use a bold condensed sans-serif font (Anton, Druk, Bebas Neue, Gotham Ultra style).
• ALL CAPS for the headline.
• Large, compact text block with tight line spacing.
• White text with a subtle drop shadow for readability.
• Keep the sub-headline smaller and visually secondary.

Effects:

• Apply a subtle dark gradient behind text.
• Add a soft vignette.
• Use light film grain and premium contrast.
• Keep overlays minimal and cinematic.
• No excessive glow, strokes, or flashy effects.

Branding:

• Place the brand logo and category tag in the top-left.
• Place the source credit in the top-right.
• Use a small colored accent bar or pill for the category label.

Quality Rules:

• Premium.
• Clean.
• Editorial.
• Professional.
• Timeless.
• Never looks like a Canva template or YouTube thumbnail.

========================
USER INPUT
========================

MAIN HEADLINE:

GAVI COLORED HIS HAIR PINK

SUB-HEADLINE:
HE KEPT HIS PROMISE
BRAND NAME

Football Insider

CATEGORY:


SOURCE:
Fabrizio Romano


COLOR PALETTE:

Primary: PINK

Secondary: WHITE

Accent: Ash and white

Text: poppins

Overlay: PINK AND ASH on background

SPECIAL NOTES: 
put the headlines in the top right corner and the sub-headlines below it



AUTOMATION_PROMPT_COMPLETE_9F3A
""".strip()


# ==================================================
# FLOW EDIT PROMPT
# ==================================================

FLOW_EDIT_PROMPT = """
Change the color of the hair to black.
AUTOMATION_PROMPT_COMPLETE_9F3A
""".strip()


# ==================================================
# FLOW RATIO CHANGE PROMPT
# ==================================================

FLOW_RATIO_CHANGE_PROMPT = """
change with desire ratio but change others thing
AUTOMATION_PROMPT_COMPLETE_9F3A
""".strip()


