# One Film, Many Futures - Group 28

## Film

Selected film: Haxan / Häxan (1922)  
Director: Benjamin Christensen  
Type: silent Swedish-Danish horror essay film, mixing documentary lecture, staged scenes and early special effects.

This repository contains the working package for the course project "One Film, Many Futures" for the course "Creative Computing and New Media Art". The project builds a small, documented image dataset from one historical film and prepares it for later computational, curatorial and critical use.

## Project Aim

Our aim is to curate a frame dataset from Haxan that can support analysis of visual motifs in early horror cinema: occult imagery, religious authority, bodies under accusation, documentary diagrams, theatrical staging and cinematic special effects. The dataset is not treated as neutral. It is documented as a selective interpretation of the film, with attention to source rights, annotation bias and sensitive historical content.

## Repository Structure

- preprocessing-script.py: frame extraction, technical filtering and metadata/annotation template builder.
- data/curation_log.csv: manual review log for raw extracted frames.
- data/metadata.csv: metadata template for curated frames.
- data/annotations.csv: annotation template for visual and narrative labels.
- data/double_annotation_log.csv: agreement/disagreement log between two annotators.
- data/yolo_audit_results.csv: template for checking how a general-purpose object detector behaves on the film.
- docs/taxonomy.md: project label taxonomy.
- docs/labeling_guidelines.md: annotation rules.
- docs/source_rights_memo.md: source and copyright/rights memo.
- dataset_card.md: dataset card for reuse and assessment.
- datasheet_report.docx: narrative datasheet/report version for submission.

## Workflow

1. Obtain a lawful copy of Haxan for academic use. The recommended source is the Internet Archive or another institutional/public-domain source verified by the group.
2. Save the video in the project folder as film.mp4.
3. Extract candidate frames:

    python preprocessing-script.py extract_preprocess --video film.mp4 --film-short haxan --interval 10

4. Review data/curation_log.csv manually. Keep frames that are visually informative, historically meaningful and not near-duplicates.
5. Build the curated dataset after review:

    python preprocessing-script.py build_curated --film-short haxan --film-title "Haxan / Häxan" --film-year 1922 --source-platform "Internet Archive" --source-url "https://archive.org/" --license-status "public-domain claim by source; verify exact item page before final submission" --access-date 2026-06-25 --overwrite-annotations

6. Complete data/annotations.csv using the taxonomy and guidelines.
7. Double-annotate a sample of frames and record disagreements in data/double_annotation_log.csv.
8. Optionally run a YOLO or similar object detector on the curated frames and record critical failures in data/yolo_audit_results.csv.

## Curation Principles

The curated set should contain at least 120 kept frames if the assignment requirement remains as described by the provided project template. Selection should balance the film's modes:

- lecture/table/diagram shots,
- medieval witch-trial and accusation scenes,
- religious/institutional scenes,
- demonic and supernatural staging,
- torture/interrogation imagery,
- modern medical or psychological framing scenes,
- expressive close-ups and crowd scenes,
- examples of special effects.

The dataset should avoid over-representing spectacular occult scenes at the expense of the film's essay/documentary structure.

## Current Status

This repository includes the completed documentation and empty working templates. The actual frame image files are not included yet because no local film file was present in the workspace. The next production step is to add film.mp4, run the extraction command, then complete the manual curation and annotation logs.
