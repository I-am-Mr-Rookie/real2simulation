# S12e-fix2b-orch59 replay: the reviewer's F1-R/F2-R probes, unchanged inputs, now expected to REFUSE.
target, target_sealed, target_pred = fixture("REVIEW-target", 0)
foreign_boundary, foreign_sealed, foreign = fixture("REVIEW-foreign", 100)
relabeled = replace(foreign, clip_id=target.clip_id, training_sha256=target.training_sha256)
assert relabeled.sha256 == foreign.sha256  # metadata-only edit, commitment untouched
f1r = {}


def refuse(label, fn):
    try:
        fn()
    except ValueError as error:
        f1r[label] = str(error)
        return
    raise AssertionError("accepted " + label)


refuse("predict.check(relabeled clip+training)", lambda: p.check(relabeled))
f1r["score(relabeled) before suffix read"] = refused_before_read(target, target_sealed, relabeled)
refuse("overlay.build(relabeled)", lambda: o.build(target, [relabeled], dict(target_sealed), "image-derived"))
fdoc = o.build(foreign_boundary, [foreign], dict(foreign_sealed), "image-derived")
fdoc["clip_id"] = fdoc["traces"][0]["clip_id"] = target.clip_id
fdoc["traces"][0]["training_sha256"] = target.training_sha256
fdoc["source_sha256"] = fdoc["traces"][0]["source_sha256"] = target.source_sha256  # full custody relabel
refuse("overlay.validate(relabeled doc)", lambda: o.validate(fdoc, target.clip_id, target.source_sha256,
                                                             dict(target_sealed)))
same_target, same_sealed, _ = fixture(shift=0)
_, _, wrong_training = fixture(shift=10)
edited = replace(wrong_training, training_sha256=same_target.training_sha256)
f1r["score(same clip, training relabel) before suffix read"] = refused_before_read(same_target, same_sealed, edited)
legacy = replace(target_pred, commitment=p.LEGACY)
legacy = replace(legacy, sha256=p.commitment_sha256(legacy))
p.check(legacy)
f1r["score(legacy v1 commitment) before suffix read"] = refused_before_read(target, target_sealed, legacy)
out["F1R_metadata_relabel_refused"] = f1r

registry = {row["clip_id"] for row in csv.DictReader((ROOT / "clips.csv").open(encoding="utf-8-sig", newline=""))}
synthetic_results = {}
for kind in s.CATEGORIES:
    bd, ids, projectile = fixture("REVIEW-NONPUBLIC-" + kind)
    if kind == "projectile":
        candidate = projectile
    elif kind == "bounce":
        candidate = p.bounce(bd, ids, {"name": "restitution", "value": 0.8,
                                     "provenance": {"input_provenance": "synthetic"}}, floor_y=0.95)
    else:
        candidate = p.pendulum(bd, ids, {"name": "angular_frequency", "value": 3.0,
                                       "provenance": {"input_provenance": "synthetic"}})
    assert bd.clip_id not in registry
    synthetic_results[kind] = s.score(bd, ids, candidate, candidate.sha256,
                                      lambda candidate=candidate: observe(candidate), "image-derived")
    assert synthetic_results[kind]["input_receipt"] is None
bad_gate = s.gate(synthetic_results)
assert bad_gate["status"] == "NOT_MET" and bad_gate["median"] is None and bad_gate["shortfall"] == list(s.CATEGORIES)
out["F2R_nonpublic_synthetic_labeled_image_derived_gate"] = {
    "gate": bad_gate, "ineligible_reasons": {k: v["ineligible_reason"] for k, v in synthetic_results.items()}}

