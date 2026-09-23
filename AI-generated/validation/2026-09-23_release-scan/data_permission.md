# Data files in the tracked tree, and the governance statement in each folder's provenance.md

## Imported data (Archive/)

### Archive
- Archive/lao-dataset/chap_LAO_admin1_monthly.csv
- Archive/lao-dataset/chap_LAO_admin1_monthly.geojson
- Archive/lao-population/worldbank_SP.POP.TOTL_LAO_1990-2021.json
- Archive/sibling-datasets/tha/chap_THA_admin1_monthly.csv
- Archive/sibling-datasets/tha/chap_THA_admin1_monthly.geojson
- Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.csv
- Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.geojson
provenance: NONE FOUND

### Archive/lao-dataset
- Archive/lao-dataset/chap_LAO_admin1_monthly.csv
- Archive/lao-dataset/chap_LAO_admin1_monthly.geojson
provenance: Archive/lao-dataset/provenance.md
    21:licence/governance:  public and redistributable (plan §4). Nothing here is
    22-                     access-restricted, so the release scan is about secrets, not
    23-                     permissions.
    --
    86:The `licence/governance:` line above says "public and redistributable (plan §4)"; that is the
    87:plan's human-set governance decision, not a licence. Checked at release time (agent-retrieved,
    88-via the GitHub API and the OpenDengue website, 2026-09-23):
    89-
    90:- The source repository `github.com/dhis2/climate-health-data` carries **no licence file**
    91:  (GitHub reports `license: null`; its top level holds `README.md`, `.gitignore` and the three
    92-  country folders). Its README states that it "contains data only", publishes "final,
    93-  model-ready data artifacts" that "can be downloaded and consumed directly by Chap", and that
    --
    99:- **OpenDengue's website states "Content licensed under CC BY 4.0"** (The Dengue Mapping and
    100-  Modelling Group, LSHTM). Redistribution of the case counts is therefore permitted with
    101-  attribution, and this section is that attribution: dengue case data from OpenDengue
    --
    109:This repository's own `LICENSE` (CC BY 4.0) applies to the derived results, not to the imported
    110-files, which remain under their upstream terms.
    111-
    112:**agency:** agent-autonomous (the check and its recording); the governance decision it
    113-qualifies is the plan's (human-set, 2026-09-20). **information:** agent-retrieved.

### Archive/lao-population
- Archive/lao-population/worldbank_SP.POP.TOTL_LAO_1990-2021.json
provenance: Archive/lao-population/provenance.md
    22:licence/governance:  CC BY 4.0. Public and redistributable, like everything else here,
    23-                     so the release scan is about secrets, not permissions.
    24-```

### Archive/sibling-datasets
- Archive/sibling-datasets/tha/chap_THA_admin1_monthly.csv
- Archive/sibling-datasets/tha/chap_THA_admin1_monthly.geojson
- Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.csv
- Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.geojson
provenance: Archive/sibling-datasets/provenance.md
    22:licence/governance:  public and redistributable (plan §4), on the same terms as the Lao
    23-                     files. Nothing here is access-restricted.
    24-```
    --
    112:repository carries no licence file and describes itself as data published for direct download;
    113-each schema attributes `disease_cases` to OpenDengue, whose website states CC BY 4.0
    114-(LSHTM). Attribution as in `Archive/lao-dataset/provenance.md`, 2026-09-23 section. **These two

### Archive/sibling-datasets/tha
- Archive/sibling-datasets/tha/chap_THA_admin1_monthly.csv
- Archive/sibling-datasets/tha/chap_THA_admin1_monthly.geojson
provenance: Archive/sibling-datasets/provenance.md
    22:licence/governance:  public and redistributable (plan §4), on the same terms as the Lao
    23-                     files. Nothing here is access-restricted.
    24-```
    --
    112:repository carries no licence file and describes itself as data published for direct download;
    113-each schema attributes `disease_cases` to OpenDengue, whose website states CC BY 4.0
    114-(LSHTM). Attribution as in `Archive/lao-dataset/provenance.md`, 2026-09-23 section. **These two

### Archive/sibling-datasets/vnm
- Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.csv
- Archive/sibling-datasets/vnm/chap_VNM_admin1_monthly.geojson
provenance: Archive/sibling-datasets/provenance.md
    22:licence/governance:  public and redistributable (plan §4), on the same terms as the Lao
    23-                     files. Nothing here is access-restricted.
    24-```
    --
    112:repository carries no licence file and describes itself as data published for direct download;
    113-each schema attributes `disease_cases` to OpenDengue, whose website states CC BY 4.0
    114-(LSHTM). Attribution as in `Archive/lao-dataset/provenance.md`, 2026-09-23 section. **These two

## Derived data (analysis/**/results/) — produced here from the imported data above
count: 276 tracked result files

## Files a data-permission reader should know are NOT tracked
- .env: not present
- .claude/settings.local.json: present in the working tree, gitignored, not tracked
