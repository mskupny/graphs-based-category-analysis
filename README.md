# Graph-Based Safety Category Assessment: Supplementary Data and Code

Supplementary material for the paper:

> **Graph-Based Numerical Method for Safety Category Assessment in Industrial Control Systems**
> Michał Skupny, Institute of Robotics and Machine Intelligence, Poznan University of Technology.

The repository contains the JSON encodings of the 13 BGIA reference circuits used in the
paper, graph figures, and the script that reproduces all results reported in the paper
(classification and the exhaustive perturbation study).

## Contents

| Path | Description |
|------|-------------|
| `graphs/SF_xx_catY.json` | Encoding of circuit SFxx (reference category Y): elements and connections. |
| `graphs/*.png` | Schematics adapted from the BGIA report and the generated graph figures. |
| `structural_classifier.py` | Classification (Section 3) and perturbation study (Section 4.4). |
| `LICENSE` | License terms (see **License** below). |

Circuits: SF01 (B), SF04, SF05, SF06, SF07, SF08 (1), SF09 (2), SF10, SF17 (1 and 3),
SF18, SF20, SF21 (3), SF28 (4).

## Reproducing the results

Requires Python 3.9+ and NetworkX.

```
pip install networkx
python structural_classifier.py classify "graphs/*.json"   # Tables 3 and 4
python structural_classifier.py perturb  "graphs/*.json"   # Table 5 (1609 variants)
```

## Encoding

Each file contains `metadata`, `elements`, and `connections`:

```json
{
  "metadata": { "sf_id": "SF_18", "category": "3" },
  "elements": [
    { "id": "B1.1", "IO": "Input", "name": "Door switch channel 1" },
    { "id": "K1",   "IO": "Logic", "name": "Safety PLC" },
    { "id": "Q1",   "IO": "Logic", "name": "Contactor 1" }
  ],
  "connections": [
    { "from": "B1.1", "to": "K1", "type": "safety_input" },
    { "from": "K1",   "to": "Q1", "type": "safety_output" },
    { "from": "Q1",   "to": "K1", "type": "feedback" }
  ]
}
```

- Element roles (`IO`): `Input`, `Logic`, `Output`, `EndEffector` (actuator and supply
  terminals), `Accessory` (passive parts). Output-stage elements may be typed `Output` or
  `Logic`; the classification does not depend on this choice.
- Connection types: `control`, `safety_input`, `safety_output`, `power`, `feedback`, and
  auxiliary types (`parallel`, `protective`, `brake`) that are not used by the analysis.
- Contacts of one device share its designation and carry a channel suffix (`B1.1`, `B1.2`);
  they are merged into one functional node during the analysis.

## Source and attribution

The circuits are adapted from the reference safety functions documented in:

> Hauke, M., Schäfer, M., Apfeld, R., et al. *Functional Safety of Machine Controls:
> Application of EN ISO 13849.* BGIA Report 2/2008e, IFA, Sankt Augustin, Germany (2008).

The original schematics remain the intellectual property of the IFA (Institut für
Arbeitsschutz der Deutschen Gesetzlichen Unfallversicherung). The adapted schematics are
provided for research reproducibility only.

## License

The author's own contribution (the JSON encodings, the generated graph figures, the code,
and the organization of the material) is released under the Creative Commons Attribution
4.0 International (CC BY 4.0) license; see `LICENSE`. The license does not extend to the
underlying BGIA/IFA source material.
