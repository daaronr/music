flowchart TD
    A(I7) --> B(I7)
    B -->|3rd Variation| C(IV7)
    B -->|Other Variations| D(I7)
    C --> E(I7)
    D --> E
    E --> F(I7)
    F --> G(IV7)
    G --> H(IV7)
    H --> I(I7)
    I --> J(I7)
    J -->|2nd Variation| K(IV7)
    J -->|4th, 5th, 6th Variations| L(VI7)
    J -->|1st, 3rd, 7th, 8th Variations| M(V7)
    K --> N(I7)
    L --> O(II7 / ii-7)
    M --> N
    N -->|2nd Variation| P(V7)
    N -->|4th, 5th, 6th Variations| Q(V7)
    N -->|1st, 3rd, 7th, 8th Variations| R(I7)
    O --> Q
    P --> R
    Q --> R
    R -->|5th Variation| S(ii- V7)
    R -->|6th Variation| T(bVI7 V7)
    R -->|7th, 8th Variations| U(iii- VI7, ii- V7)
    R -->|1st, 2nd, 3rd, 4th Variations| V(V7)

    classDef variation fill:#f9f,stroke:#333,stroke-width:2px;
    class C,L,K,O variation;

