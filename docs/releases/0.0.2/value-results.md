# Product value benchmark

Version: 0.0.2. Suite: `product-value-v1`. Evidence: complete.

Each row compares the same tasks and model. Timing uses only pairs solved by both conditions; failures and uncompleted trials remain in the inventory. Different models are reported separately.

Report each model and task family separately. Shared provider concurrency affects observed delivery time.

DP2 repetition 1 uses physical devices 8/9 for G0 and 12/13 for G1/G2 after an unrelated workload occupied device 8. The other workload was not modified. These observations do not isolate physical-device placement effects.

Plugin task comparisons use native hosts, controlled MCP registration and shipped Skills. Full plugin lifecycle acceptance is reported separately.

G0 uses the native host. G1 adds remote-dev. G2 also adds knowledge retrieval, shipped Skills and explicit retrieval guidance. G3 captures an earlier task for later reuse. G1/G2 therefore measures that combined guidance and retrieval condition, not the isolated retrieval implementation.

| Study | Model | Observed / planned | Pass | Fail | Infrastructure | Unknown |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| dp2 | home/codex/gpt-6.1-sol | 9 / 9 | 7 | 2 | 0 | 0 |
| stale | home/codex/gpt-6.1-sol | 6 / 6 | 6 | 0 | 0 | 0 |
| quarot | home/codex/gpt-6.1-sol | 9 / 9 | 9 | 0 | 0 | 0 |
| claude-code | deepseek-flash | 6 / 6 | 4 | 2 | 0 | 0 |
| dsh | deepseek-flash | 6 / 6 | 5 | 1 | 0 | 0 |
| kimi | k3 | 6 / 6 | 3 | 3 | 0 | 0 |
| knowledge-transfer | home/codex/gpt-6.1-sol | 27 / 27 | 27 | 0 | 0 | 0 |

## Measurement versions and scope

Release runner: mindie-bench 0.3.0 at `18a19aa582d55d3c6eba2544f9dae002dcec1215`. Tasks ran on the earlier versions listed below. Later infrastructure, cleanup and publication changes do not represent new task measurements or identical setup timing.
- trial `0.2.0 at fe87041b0c78730c04b8c67e287e0a82a017b4e6`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.2.0 at 7af0088da289c45a84dfecca699b7f442943b695`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.3.0 at 175a6f4db27701739d2615e8de53fa24c96e2dc0`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.2.0 at 03e74644d4d2a118ebad5d6d10db67b0ea989b75`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.2.0 at cb59dcef0222648e65afe11d157c11f5304a86b6`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.3.0 at 9acb27727785c318832c774325acb7b090e42e72`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.2.0 at revision unrecorded`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- trial `0.2.0 at 242ef494b099bd82d3d34c33dea61a2b044a2eaa`: The recorded runner and original task result are retained. Earlier gateway, native-host and cleanup repairs are disclosed in the runner patch history. Later changes separate local evidence errors from lease cleanup, serialize short Git metadata edits, repair installed-package provenance and bind publication to reviewed sources. These are measurement infrastructure and delivery changes, not new measurements of the final runner. Task inputs, models, budgets, treatment components and recorded costs are not rewritten.
- component `component scenario sources retained in the data`: The original runner checkout observations are retained, including any dirty state or changed revision. They do not establish an exact final runner measurement. The scenarios use the separately recorded noneditable component revisions; the final coordinator scenario has its own source record. Later runner changes repair package-origin discovery and report publication, without changing these scenario outcomes or measurements.
- component `component scenario sources retained in the data`: The original runner checkout observations are retained, including any dirty state or changed revision. They do not establish an exact final runner measurement. The scenarios use the separately recorded noneditable component revisions; the final coordinator scenario has its own source record. Later runner changes repair package-origin discovery and report publication, without changing these scenario outcomes or measurements.

## Reviewed benchmark infrastructure changes

These are changed instrumentation sources, not identical-code claims. The mappings apply only to the listed studies; raw receipt identities and original attempt costs are retained. Component scenarios still require the exact release source.
- coordinator: `daf7fa38b431187c04a6dea4341df4a066100953` to `34812c2d385f3ff112be3a597d27fd3a0c15c104`; studies: dp2, stale, quarot. Reviewed lease-instrumentation repair: retain exclusive idle admission, but release a completed managed owner after exact guard, epoch, fence and port checks even when unrelated workloads occupy the device. Coordinator is not a G0/G1/G2 treatment component. Earlier receipts keep their original revision; the component scenario uses the final source. Original contaminated timings remain excluded with all costs retained.

## dp2

Real historical task under the native Codex host with controlled MindIE MCP and shipped Skills.

- G0 to G2: 3 valid pairs; 2 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.975x.
- G0 to G1: 3 valid pairs; 1 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.963x.
- G1 to G2: 3 valid pairs; 2 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.789x.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 | 4 | 2 | 1934.67 | 444645 | 7590528 | 60128 | 0 | False |
| G1 | 5 | 2 | 2864.28 | 820033 | 11837440 | 82225 | 0 | True |
| G2 | 5 | 3 | 2981.92 | 1053721 | 15671808 | 86952 | 0 | True |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

Original recorded first-attempt outcomes: completed_pass=4, infra_failed=1, unknown=2, completed_fail=2. Paired timing uses the selected settled attempts; totals also include the original infrastructure failures and explicit recovery attempts.

## stale

Real historical task under the native Codex host with controlled MindIE MCP and shipped Skills.

- G1 to G2: 3 valid pairs; 3 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.595x.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G1 | 3 | 3 | 797.23 | 173952 | 1556736 | 8179 | 0 | True |
| G2 | 5 | 3 | 1930.22 | 504486 | 7254400 | 36835 | 0 | False |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

Original recorded first-attempt outcomes: completed_pass=4, unknown=2. Paired timing uses the selected settled attempts; totals also include the original infrastructure failures and explicit recovery attempts.

## quarot

Real historical task under the native Codex host with controlled MindIE MCP and shipped Skills.

- G0 to G2: 3 valid pairs; 3 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.689x.
- G0 to G1: 3 valid pairs; 3 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 1.025x.
- G1 to G2: 3 valid pairs; 3 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.673x.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 | 4 | 3 | 747.31 | 244002 | 1314688 | 26739 | 0 | False |
| G1 | 3 | 3 | 550.89 | 193466 | 983168 | 20914 | 0 | True |
| G2 | 3 | 3 | 818.72 | 233487 | 1977984 | 28199 | 0 | True |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

Original recorded first-attempt outcomes: completed_pass=8, unknown=1. Paired timing uses the selected settled attempts; totals also include the original infrastructure failures and explicit recovery attempts.

## claude-code

Native host with controlled MCP and the released plugin Skills. Full plugin loading is verified separately.

- G0 to G2: 3 valid pairs; 2 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.678x.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 | 4 | 2 | 262.58 | 134223 | 1870208 | 37158 | 0 | False |
| G2 | 4 | 2 | 468.84 | 395000 | 6527872 | 59533 | 0 | False |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

Original recorded first-attempt outcomes: completed_pass=4, unknown=2. Paired timing uses the selected settled attempts; totals also include the original infrastructure failures and explicit recovery attempts.

## dsh

Native host with controlled MCP and the released plugin Skills. Full plugin loading is verified separately.

- G0 to G2: 3 valid pairs; 2 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.600x.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 | 3 | 2 | 321.08 | 148644 | 2995584 | 49761 | 0 | True |
| G2 | 3 | 3 | 467.65 | 347179 | 7276672 | 52928 | 0 | True |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

## kimi

Native host with controlled MCP and the released plugin Skills. Full plugin loading is verified separately.

- G0 to G2: 3 valid pairs; 0 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: unmeasured.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 | 4 | 2 | 1111.07 | 84408 | 1815808 | 38599 | 0 | False |
| G2 | 4 | 1 | 2365.33 | 222176 | 3799296 | 46819 | 0 | False |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

Original recorded first-attempt outcomes: unknown=1, completed_pass=2, completed_fail=3. Paired timing uses the selected settled attempts; totals also include the original infrastructure failures and explicit recovery attempts.

An original completed_fail record was confirmed to be a zero-model native startup failure. Its raw label and costs remain in historical evidence; it is excluded from task comparisons.

## knowledge-transfer

One historical publication task seeds two distinct later publication tasks. Seed execution and capture are included in total workflow costs. This is within-project transfer, not evidence of cross-project generalization.

- G1 to G2: 6 valid pairs; 6 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 0.685x.
- G2 to G3: 6 valid pairs; 6 solved by both.
  Paired evaluation delivery-time baseline/candidate ratio: 1.011x.

| Condition | Selected + historical attempts | Selected solved | Total delivery seconds | Uncached input | Cached input | Output | Capture tokens | Metering complete |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G1 | 12 | 9 | 2612.57 | 789740 | 5611776 | 113980 | 0 | True |
| G2 | 14 | 9 | 4140.76 | 1368585 | 12203392 | 135964 | 0 | False |
| G3 | 12 | 9 | 3312.74 | 1013810 | 8324480 | 107700 | 112646 | False |

Totals include failed attempts and, for the transfer workflow, the seed task and capture. These workflow totals are distinct from evaluation-only paired timing. Incomplete totals are lower bounds. Token categories are kept separate; absent prices do not imply zero dollar cost.

Original recorded first-attempt outcomes: completed_pass=24, unknown=3. Paired timing uses the selected settled attempts; totals also include the original infrastructure failures and explicit recovery attempts.

| Repetition | Evaluation | Seed returned by query | Seed read through explain |
| ---: | --- | --- | --- |
| 1 | publication-flush-eval | True | True |
| 1 | publication-submit-eval | True | True |
| 2 | publication-flush-eval | True | True |
| 2 | publication-submit-eval | True | True |
| 3 | publication-flush-eval | False | False |
| 3 | publication-submit-eval | True | True |

A captured seed being available does not imply the agent used it. Missing retrieval is retained as an observed result.

## npu-top

physical die/PID/HBM correctness from captures and live proc/container identity

Measured repetitions: 3.

- A2 live and A3 dual-die historical captures are reported separately.
- Golden replay repetitions measure repeatability, not independent hardware samples.
- The container identity probe does not claim its init process consumes NPU memory.
- No model/human task timing, avoided incident count or causal productivity gain is measured.
- Raw command lines, working directories and environments are not exported.

| Observation | Baseline samples | Candidate samples |
| --- | --- | --- |
| golden_physical_devices_correct | unmeasured, unmeasured, unmeasured | 24, 24, 24 |
| golden_process_assignments_correct | unmeasured, unmeasured, unmeasured | 16, 16, 16 |
| golden_process_assignments_expected | unmeasured, unmeasured, unmeasured | 16, 16, 16 |
| human_answer_accuracy | None, None, None | unmeasured, unmeasured, unmeasured |
| human_completion_time_sec | None, None, None | unmeasured, unmeasured, unmeasured |
| live_container_owner_correct | unmeasured, unmeasured, unmeasured | True, True, True |
| live_physical_devices | unmeasured, unmeasured, unmeasured | 8, 8, 8 |
| live_ssh_operations | unmeasured, unmeasured, unmeasured | 3, 3, 3 |

## diagnostics

real logging, linked consent, ingestion, outbox and reporter with local HTTP

Measured repetitions: 3.

- The HTTP receiver implements a bounded GitHub-compatible fixture, not GitHub availability.
- GitHub.request and subprocess parsing are production code; only its executable transport is local.
- The controlled fault is FileNotFoundError; reporting does not repair the failing operation.
- No human triage-time or model productivity claim is made.
- The separate public Issue 243 native canary is not rerun or counted here.

| Observation | Baseline samples | Candidate samples |
| --- | --- | --- |
| automatic_delivery | False, False, False | unmeasured, unmeasured, unmeasured |
| contains_synthetic_secret | True, True, True | unmeasured, unmeasured, unmeasured |
| delivered_reports | unmeasured, unmeasured, unmeasured | 1, 1, 1 |
| failure_occurrences | 3, 3, 3 | 3, 3, 3 |
| failure_to_delivery_sec | unmeasured, unmeasured, unmeasured | 60.58435137500055, 60.583874207979534, 60.64036570902681 |
| http_posts | unmeasured, unmeasured, unmeasured | 1, 1, 1 |
| private_fixture_removed | unmeasured, unmeasured, unmeasured | True, True, True |
| production_retry_wait_sec | unmeasured, unmeasured, unmeasured | 59.99844813346863, 59.998303174972534, 59.99814820289612 |
| queue_items | unmeasured, unmeasured, unmeasured | 1, 1, 1 |
| raw_tracebacks | 3, 3, 3 | unmeasured, unmeasured, unmeasured |
| reconciled_without_duplicate | unmeasured, unmeasured, unmeasured | True, True, True |
| useful_fault_fields_retained | unmeasured, unmeasured, unmeasured | True, True, True |
| withdrawal_prevented_requests | unmeasured, unmeasured, unmeasured | True, True, True |

## coordinator

two concurrent agents, live TCP ports, production SQLite allocation and recovery

Measured repetitions: 3.

- This is the check-then-act race, not a comparison against another atomic scheduler.
- Device identities come from observation; no NPU compute is launched or reserved globally.
- Ports, child processes and allocation state are owned by this local scenario.
- Elapsed time includes child startup and is not a model productivity estimate.

| Observation | Baseline samples | Candidate samples |
| --- | --- | --- |
| bind_conflicts | 1, 1, 1 | 0, 0, 0 |
| duplicate_device_selections | 1, 1, 1 | 0, 0, 0 |
| elapsed_sec | 0.040280334011185914, 0.03515266702743247, 0.03628624998964369 | 0.04837987496284768, 0.047501625027507544, 0.04742216697195545 |
| release_to_next_success_sec | None, None, None | 0.002114624949172139, 0.0018486669869162142, 0.0019109999993816018 |
| successful_listeners | 1, 1, 1 | 2, 2, 2 |

## Setup and diagnostic model usage

These separately measured operations are additional execution costs. They are excluded from task success rates and paired task timing. Missing duration or price remains unmeasured.

| Plugin | Operation | Seconds | Uncached input | Cached input | Output |
| --- | --- | ---: | ---: | ---: | ---: |
| codex | native summary catalog repair acceptance | 4.947 | 10501 | 0 | 202 |
| codex | native summary continuation diagnosis | unmeasured | 11072 | 0 | 301 |
| codex | native summary continuation diagnosis | unmeasured | 11069 | 0 | 693 |
| kimi | native OAuth refresh inference | 9.103719000006095 | 3778 | 23296 | 53 |
| kimi | native OAuth refresh inference | 5.9777257919777185 | 3537 | 23552 | 48 |
| kimi | native OAuth refresh inference | 5.28738162497757 | 3537 | 23552 | 40 |
| kimi | native OAuth refresh inference | 5.435405750002246 | 3537 | 23552 | 34 |

## Excluded attempts

These attempts remain in the evidence with their measured resource costs.
- `l2-quarot-draft-dispatch_G0_1_23d6f3e16e3f`: Single affected-cell retest after actual native FSEvents startup failure was reproduced and repaired; no task/model/budget change. Original receipt and elapsed/token uncertainty retained.
- `l2-quarot-draft-dispatch_G2_1_c5622da1aa87`: Single affected-cell retest after actual native FSEvents startup failure was reproduced and repaired; no task/model/budget change. Original receipt and elapsed/token uncertainty retained.
- `l2-quarot-draft-dispatch_G0_3_fc8e598bcdf8`: User-authorized single-cell retest after safe TLS stage logging and 3 passing TLS-only probes.
- `l2-quarot-draft-dispatch_G2_3_6629b6c3061d`: User-authorized single-cell retest after safe TLS stage logging and 3 passing TLS-only probes.
- `k3-gdn-idle-dp-state_G0_1_c2f7c5507784`: Protected-runtime read grant rejected before native harness/model startup. This historical setup failure is not a control-equivalent task attempt.
- `k3-gdn-idle-dp-state_G1_1_de80ac2f341b`: Business oracle passed, but foreign device ownership invalidated postflight; moved slot.
- `k3-gdn-idle-dp-state_G1_2_87b4ffed70e3`: Whole-cell retest after foreign workload interruption and owned namespace reconciliation.
- `k3-gdn-idle-dp-state_G2_2_69aa82fdc302`: Whole-cell retest after foreign workload interruption and exact owned lease reconciliation.
- `k3-gdn-idle-dp-state_G2_2_a68ea09e6ce3`: One whole-cell retest after repairing owned-cleanup classification and guarded coordinator completion; exact historical leases released, no request replay.
- `stale-fused-mc2-deployment_G2_1_81c9ce94c402`: Whole-cell retest after repairing not_sent heartbeat classification; no request replay.
- `stale-fused-mc2-deployment_G2_3_9daee763b3ba`: One authorized whole-cell retest after incomplete provider stream; no request replay.
- `l2-quarot-draft-dispatch_G0_3_821a30387312`: One whole-cell retest after incomplete provider stream; no request replay.
- `publication-export-seed_G1_1_d6c969aa40bf`: invalid_task_contract
- `publication-export-seed_G1_2_47eb6368b1c7`: invalid_task_contract
- `publication-export-seed_G1_3_b72eb9229388`: invalid_task_contract
- `publication-export-seed_G2_1_9594390dab0a`: invalid_task_contract
- `publication-export-seed_G2_2_124b8817355f`: invalid_task_contract
- `publication-export-seed_G2_3_ec90b3897292`: invalid_task_contract
- `publication-flush-eval_G2_2_bf8e903f3edc`: provider_stream_eof_incomplete_usage; explicit_single_cell_retest_authorized
- `publication-export-seed_G3_1_2c589185f6ef`: invalid_task_contract; capture_integration_failure
- `publication-export-seed_G3_2_f8711ba2d96e`: invalid_task_contract; operator_cancelled
- `publication-submit-eval_G3_1_263c10f0416b`: capture_request_budget_exhausted; explicit_single_cell_retest_authorized
- `publication-export-seed-v2_G2_1_2b6a13bcd61b`: provider_stream_ended_incomplete_usage; explicit_single_cell_retest_authorized
