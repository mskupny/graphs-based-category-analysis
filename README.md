# Graph-Based Safety Category Assessment — Supplementary Data

Supplementary material for the paper:

> **Graph-Based Numerical Method for Safety Category Assessment in Industrial Control Systems**
> Michał Skupny, Institute of Robotics and Machine Intelligence, Poznan University of Technology.

This repository contains the machine-readable circuit encodings and the corresponding
graph representations for the fifteen reference safety functions used to validate the
method described in the paper.

---

## Contents

| Path | Description |
|------|-------------|
| `json/` | JSON encodings of each safety circuit (components and connections). |
| `figures/` | Circuit diagrams and their corresponding directed-graph representations. |
| `README.md` | This file. |
| `LICENSE` | License terms (see **License** below). |

Each safety function is identified by its BGIA reference designation (e.g. `SF01`, `SF05`,
`SF17`, `SF18`). For every function the repository provides:

- a JSON file encoding the circuit as an `elements` array (components) and a
  `connections` array (directed edges), and
- a side-by-side pair of images: the adapted schematic and the generated graph
  representation.

## JSON schema

Each JSON file describes one safety circuit with two arrays:

```json
{
  "elements": [
    { "id": "B1.1", "type": "Input",  "IO": "out",    "description": "Position switch, guard ch. 1" },
    { "id": "K1",   "type": "Logic",  "IO": "in/out", "description": "Safety PLC" },
    { "id": "Q1",   "type": "Output", "IO": "in/out", "description": "Contactor 1" }
  ],
  "connections": [
    { "from": "B1.1", "to": "K1", "type": "control" },
    { "from": "K1",   "to": "Q1", "type": "safety_output" },
    { "from": "Q1",   "to": "K1", "type": "feedback" }
  ]
}
```

- **`type`** (element) ∈ `Input`, `Logic`, `Output`, `EndEffector`
- **`type`** (connection) ∈ `control`, `power`, `feedback`, `safety_output`
- Component identifiers follow IEC 81346 designation principles. All references in
  `connections` correspond to defined `elements` (referential integrity).

## Source and attribution

The circuit diagrams are adapted from the reference safety functions documented in:

> Hauke, M., Schäfer, M., Apfeld, R., et al. *Functional Safety of Machine Controls —
> Application of EN ISO 13849.* BGIA Report 2/2008e, IFA, Sankt Augustin, Germany (2008).

The original schematics remain the intellectual property of the IFA (Institut für
Arbeitsschutz der Deutschen Gesetzlichen Unfallversicherung). The adapted schematics
are provided here for research reproducibility only; rights to the underlying source
material are retained by their original holder.

## How to cite

If you use these data, please cite the associated paper. A `CITATION.cff` file will be
added upon publication.

## License

The **original contribution** of this repository — the JSON encodings, the generated
graph representations, and the organization of the material — is released under the
**Creative Commons Attribution 4.0 International (CC BY 4.0)** license; see the
[`LICENSE`](LICENSE) file.

This license applies only to the author's own contribution. It does **not** extend to
the underlying BGIA/IFA source material adapted in the schematic images, whose rights
are retained by their original holder (see **Source and attribution** above).
