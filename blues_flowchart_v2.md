graph TD
    A(I7) --> B(I7/IV7)
    B -->|I7| C(I7)
    B -->|IV7| D(IV7)
    C --> E(I7)
    D --> E
    E --> F(IV7)
    F --> G(IV7/I7/VII7)
    G -->|IV7| H(IV7)
    G -->|I7| I(I7)
    G -->|VII7| J(VII7)
    H --> K(I7)
    I --> K
    J --> K
    K --> L(I7/VI7/v-/iii-)
    L -->|I7| M(V7)
    L -->|VI7| N(VI7)
    L -->|v-| O(v- I7)
    L -->|iii-| P(iii- VI7)
    M --> Q(V7)
    N --> R(II7/bVI7)
    O --> S(VII7)
    P --> T(ii-7)
    Q --> U(I7)
    R --> U
    S --> U
    T --> U
    U --> V(V7/ii- V7/bVI7 V7)
    V --> W(I7/vi7/iii- VI7)
    W --> X(I7)

    classDef default fill:#f9f,stroke:#333,stroke-width:2px;
    classDef var fill:#bbf,stroke:#f66,stroke-width:2px,stroke-dasharray: 5, 5;
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X var;

