# Figure 3 scientific check

**Pass.** Insert the supplied schematic after the final sentence of §4.6. The artwork and the proposed callout agree with the theory.

- Panel A places a finite fitted-score reversal at bandwidth \(\sigma_w\) inside the full-width request \((0,t]\times[\lambda_0,\infty)\). Section 4.6 makes one strict included reversal sufficient to exclude uniform agreement at the fixed query. Proposition 3 supplies a finite witness when the limiting competing margin is strictly positive and the witness penalty exceeds its stated threshold.
- Panel B places that same witness below the certified bandwidth band because \(0<\sigma_w<s\leq t\). Theorem 2 guarantees the nearest-prototype class as unique winner throughout \([s,t]\) at every finite \(\lambda\geq\Lambda\), provided \(\Lambda>0\) and the strict signed inequality holds for every competitor. The panels concern different regions at the same query, so the conclusions coexist.
- The PDF and PNG show the same qualitative geometry. The axes, witness location, and penalty floors are schematic. The caption makes no claim about an observed query, fitted run, or measured parameter.

## Caption and callout

The only mathematical precision to add is the positive local floor \(\Lambda>0\), as stipulated in Theorem 2. The supplied callout can be used with a cross-reference. The following LaTeX also makes the fitted-score witness and unique winner explicit.

**Callout**

```latex
Fig.~\ref{fig:parameter-regions} shows how a strict disagreement at a bandwidth below the local band can exclude full-width agreement even when the signed test certifies the local band.
```

**Caption**

```latex
\caption{Full-width exclusion and local-band certification for the same query. (A) One finite parameter pair within the requested region, marked by a cross at bandwidth $\sigma_w$, suffices to exclude uniform nearest-prototype agreement when a competing class has a strictly larger fitted score than the nearest-prototype class. (B) With $0<\sigma_w<s\leq t$, the same disagreement falls below the bandwidth band $[s,t]$. If the signed condition in Theorem~\ref{thm:local-tail} holds against every competing class for a positive floor $\Lambda$, the nearest-prototype class is the unique winner throughout the shaded band at every finite penalty $\lambda\geq\Lambda$. Upward arrows indicate that both regions extend to arbitrarily large finite penalties. Schematic axes.}
\label{fig:parameter-regions}
```
