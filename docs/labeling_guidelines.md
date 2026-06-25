# Labeling Guidelines

## Goal
These guidelines help annotators label frames from Haxan / Häxan consistently while respecting the film's historical distance, sensitive subject matter and hybrid documentary-fiction form.

## Basic Annotation Steps
1. Look at the frame without guessing beyond what is visible.
2. Choose one primary_object_label from docs/taxonomy.md.
3. Add zero or more secondary_object_labels, separated by semicolons.
4. Choose one narrative_label.
5. Set confidence to high, medium or low.
6. Mark requires_context as yes if the label depends on knowing the scene or intertitle.
7. Add a short note when the decision is ambiguous, sensitive or context-dependent.

## What Counts as Context?

Use requires_context=yes when the frame alone does not show whether a person is accused, confessing or judging; a label depends on a previous intertitle; the frame is a diagram whose meaning is not obvious; or a role such as witch, doctor or inquisitor cannot be inferred from costume alone.

Use requires_context=no when the visual content is clear without surrounding frames.

## Handling Sensitive Content

Use descriptive language, not sensational language. Prefer torture_or_execution_device instead of graphic wording, medical_or_psychological_scene instead of diagnostic claims, witch_accused_woman instead of treating witch as a real identity, and nudity_sensitive only as a secondary label when relevant for dataset warnings.

Do not add jokes, moral judgments or speculative diagnoses in annotator notes.

## Intertitles and Text Frames

If text dominates the image, use intertitle_or_text. If the text appears inside a book or document shown as an object, use book_or_manuscript and add intertitle_or_text as a secondary label only if the readable text is important.

## Diagrams, Models and Scholarly Material

The film often uses diagrams, models and illustrations to create a lecture-like structure. Use diagram_or_model for constructed visual explanations, and book_or_manuscript for pages, engravings or source documents.

## People and Roles

When a person is central, label the role that the film visually emphasizes. Use clergy_or_inquisitor for monks, priests, judges and religious/legal authorities. Use witch_accused_woman when the scene frames a woman as accused or suspected. Use close_up_face when expression is more important than social role. Use crowd_or_mob when the group dynamic matters more than any individual.

## Special Effects

Use special_effect_shot when the main reason the frame matters is a cinematic trick: superimposition, flying, reverse motion, stop-motion-like movement, theatrical demon effects or illusion staging. If a demon is also central, put devil_or_demon as the primary label only when the figure is more important than the effect.

## Double Annotation Procedure

At least two annotators should independently label a sample of frames. Record disagreements in data/double_annotation_log.csv with frame ID, annotator A label, annotator B label, disagreement type, final resolved label and short resolution note.

Common disagreement types: object_label_disagreement; narrative_label_disagreement; confidence_disagreement; context_needed_disagreement; sensitive_content_flag.

## Quality Checklist

Before final submission, check that every curated image has one metadata row, every curated image has one annotation row, labels come from the taxonomy, uncertain labels have notes, sensitive content is flagged calmly and consistently, and the source URL and access date are recorded.
