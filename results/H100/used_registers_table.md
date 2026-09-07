# Register Allocation per Thread across Automatons and Implementations

| Automaton | Reference | Standard | Bit Packing (Array) | Bit Planes (Linear) | Bit Planes (Tiled) | Temporal Linear | Temporal Tiled |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Game Of Life (1-bit) | 25 | 24 | 32 | 30 | 32 | 48 | 46 |
| Critters (1-bit) | 29 | 25 | 32 | 32 | 40 | 48 | 48 |
| Maze (1-bit) | 26 | 24 | 32 | 26 | 30 | 48 | 48 |
| Brian (2-bit) | 25 | 28 | 32 | 32 | 32 | 63 | 65 |
| Wire (2-bit) | 28 | 28 | 32 | 32 | 40 | 63 | 63 |
| Forest Fire (2-bit) | 22 | 26 | 32 | 28 | 32 | 56 | 56 |
| Traffic (2-bit) | 23 | 20 | 30 | 30 | 25 | 64 | 40 |
| Excitable (3-bit) | 28 | 28 | 32 | 32 | 48 | 77 | 51 |
| Fluid (4-bit) | 25 | 25 | 48 | 26 | 31 | 32 | 32 |
| Cyclic (5-bit) | 26 | 26 | 32 | 64 | 72 | 56 | 78 |