# Dataset Card: Haxan / Häxan (1922) Frame Dataset

## Dataset Name

One Film, Many Futures - Haxan / Häxan (1922), Group 28

## Dataset Summary

This dataset is designed as a curated frame collection from Benjamin Christensen's Haxan / Häxan (1922). The film combines documentary-style lecture, staged historical scenes, occult horror imagery and early cinematic effects. The dataset is intended for creative computing, visual culture analysis and critical experimentation with computer vision tools.

The dataset should be built from frames extracted at regular intervals and then manually curated. It is not a full copy of the film. It is a selective visual dataset with metadata, annotation labels and documentation of curation choices.

## Intended Uses

- Study of motifs in silent horror and early documentary-fiction hybrid cinema.
- Critical comparison between human visual annotation and automated object detection.
- Creative computing projects using archival film frames as source material.
- Classroom discussion about dataset construction, bias, rights and historical context.

## Out-of-Scope Uses

- Commercial redistribution of film frames without independent rights clearance.
- Claims about medical, psychological or religious groups based only on film imagery.
- Training high-stakes recognition systems.
- Treating labels as objective facts about witchcraft, religion, gender or mental health.

## Source Material

- Film: Haxan / Häxan
- Year: 1922
- Director: Benjamin Christensen
- Production context: Swedish-Danish silent film, produced by Svensk Filmindustri and shot in Denmark.
- Proposed access source: Internet Archive or another verified public-domain/institutional source.

The source-rights reasoning is documented in docs/source_rights_memo.md.

## Collection Method

Frames are extracted with preprocessing-script.py, using ffmpeg through the script's extract_preprocess mode. The recommended interval is one frame every 10 seconds. The script records brightness, contrast, blur score and a perceptual hash distance to help reviewers identify black frames, low-contrast frames and near-duplicates.

Human reviewers then decide which candidate frames to keep. Kept frames are resized without upscaling, copied into the curated image folder and linked to metadata and annotation CSV files.

## Annotation Schema

The annotation schema combines a primary object or visual motif label, optional secondary labels, a narrative/function label, confidence, whether the image requires film context, and annotator notes.

The full taxonomy is in docs/taxonomy.md. The annotation rules are in docs/labeling_guidelines.md.

## Sensitive Content

The film includes imagery of torture and execution, religious persecution, nudity or sexualized accusation, demonological imagery, historical framing of mental illness and gendered violence. Annotations should describe what is visible and how the film frames it, without endorsing the film's historical assumptions.

## Bias and Limitations

The dataset inherits biases from the 1922 film's European cultural assumptions, its depiction of women, religion, disability and mental health, the group's frame selection, the chosen annotation vocabulary, and any automated detector tested on low-resolution monochrome/tinted silent-film imagery.

Because the film is staged and stylized, object labels may be ambiguous. A "witch", "devil" or "inquisitor" label is a role within the filmic scene, not a factual identity.

## Quality Control

Quality control should include technical filtering of unusable frames, manual curation decisions, double annotation for a sample of frames, disagreement logging, and optional object-detection auditing.

## Maintenance

This is a course dataset. If reused after submission, future maintainers should record exact source URL, access date, extraction interval, number of raw frames, number of kept frames, changes to taxonomy and any new rights review.
