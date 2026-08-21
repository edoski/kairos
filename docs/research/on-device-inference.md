# KAIROS on-device inference decision and acceptance plan

Date: 2026-07-26

## Decision

KAIROS mobile inference is a self-contained application path:

```text
public EVM JSON-RPC
        |
        v
closed-block context -> TypeScript feature transform -> bundled XNNPACK model
                                                       |
                                                       v
                                      recommendation and fee prediction
                                                       |
                                                       v
                                      local history and RPC outcomes
```

RPC supplies raw blockchain observations. Feature preparation, neural inference, decoding,
history, outcome resolution, and analytics run in the Expo app. There is no Python inference
server, remote model download, or fallback path.

This keeps the existing cross-platform React Native interface while removing the project-specific
service. A native Swift/Core ML rewrite would replace working application code and introduce a
second model interface without reducing the thesis scope.

## Repository contract

The canonical exporter and app runtime contract is owned by
[Mobile deployment](../KAIROS.md#mobile-deployment). This note records the decision rationale,
verified evidence, and remaining acceptance boundary.

## Verified boundary

The repository contains the final `MOBILE.yaml`, generated manifest, and all twelve `.pte` assets.
The exporter accepted every `(chain,K)` cell only after XNNPACK delegation and
eager-versus-ExecuTorch parity on a zero tensor and deterministic nonzero tensor. Those checks cover
both ExecuTorch outputs, the selected action, and decoded fee within the exporter's tolerance.

On 2026-08-20, a custom native iOS Simulator Release build launched the app and completed real
public-RPC recommendations for Ethereum `K=5` and Polygon `K=5`. AsyncStorage contained both
successful runs and resolved outcomes. This verifies the exercised end-to-end Simulator path, not
every bundled model.

No confidence or probability output exists. The model returns action logits and one standardized
minimum-fee prediction; the app decodes an action offset and predicted horizon-minimum base fee.

## Developer flow

The current asset-generation and custom native build instructions are owned by the
[README mobile demo](../../README.md#mobile-demo).

## Remaining acceptance

The native app has not exercised all twelve `(chain,K)` cells. A physical iPhone run has not tested
device-only latency, peak memory, or thermal behavior. Do not infer either result from exporter
parity or the two exercised Simulator cells.

## Primary references

- [Expo SDK 55](https://docs.expo.dev/versions/v55.0.0/)
- [Expo Continuous Native Generation](https://docs.expo.dev/workflow/continuous-native-generation/)
- [React Native ExecuTorch compatibility](https://docs.swmansion.com/react-native-executorch/docs/other/compatibility)
- [ExecuTorch model loading](https://docs.swmansion.com/react-native-executorch/docs/fundamentals/loading-models)
- [ExecuTorch 1.2 export](https://docs.pytorch.org/executorch/1.2/using-executorch-export.html)
- [Viem Public Client](https://viem.sh/docs/clients/public)
- [Viem fee history](https://viem.sh/docs/actions/public/getFeeHistory)
- [Ethereum execution API](https://ethereum.github.io/execution-apis/api/methods/eth_getBlockByNumber/)
