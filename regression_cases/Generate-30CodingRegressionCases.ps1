param(
  [string]$OnlyCase = ''
)
$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$moduleDir = Join-Path $repo 'custom_modules\coding_regression_30'
$caseRoot = Join-Path $repo 'regression_cases'
$manifestPath = Join-Path $caseRoot 'manifest_30.json'
$summaryPath = Join-Path $caseRoot 'validation_summary.md'

function C($code, $display) {
  return [ordered]@{ Code = $code; Display = $display }
}

function New-Case($id, $slug, $conditions, $complaint, $reasonIndex, $note, $relationships, $nonRelationships, $encounterClass = 'ambulatory', $history = @(), $currentConditions = $null) {
  if ($null -eq $currentConditions) { $currentConditions = $conditions }
  return [pscustomobject]@{
    CaseId = ('case_{0:d2}' -f $id)
    Slug = $slug
    Conditions = @($conditions)
    CurrentConditions = @($currentConditions)
    Complaint = $complaint
    ReasonIndex = $reasonIndex
    Note = $note
    Relationships = @($relationships)
    NonRelationships = @($nonRelationships)
    EncounterClass = $encounterClass
    History = @($history)
    Seed = 3000 + $id
    ClinicianSeed = 4000 + $id
  }
}

$diabetes = C '44054006' 'Diabetes mellitus type 2 (disorder)'
$ckd1 = C '431855005' 'Chronic kidney disease stage 1 (disorder)'
$ckd3 = C '433144002' 'Chronic kidney disease stage 3 (disorder)'
$hypertension = C '59621000' 'Essential hypertension (disorder)'
$obesity = C '414915002' 'Obesity (disorder)'
$hyperlipidemia = C '55822004' 'Hyperlipidemia (disorder)'
$copd = C '13630005' 'Chronic obstructive lung disease (disorder)'
$asthma = C '195967001' 'Asthma (disorder)'
$rhinitis = C '61582004' 'Allergic rhinitis (disorder)'
$heartFailure = C '84114007' 'Heart failure (disorder)'
$hypothyroidism = C '40930008' 'Hypothyroidism (disorder)'
$gerd = C '235595009' 'Gastroesophageal reflux disease (disorder)'
$osteoarthritis = C '239862000' 'Osteoarthritis of knee (disorder)'
$depression = C '35489007' 'Depressive disorder (disorder)'
$bronchitis = C '10509002' 'Acute bronchitis (disorder)'
$viralUri = C '54150009' 'Upper respiratory infection (disorder)'
$dental = C '80967001' 'Dental caries (disorder)'
$anemia = C '271737000' 'Anemia (disorder)'
$chestPain = C '29857009' 'Chest pain (disorder)'

$cases = @(
  (New-Case 1 'case_01_diabetes_single' @($diabetes) 'Follow-up for type 2 diabetes mellitus' 0 'Type 2 diabetes mellitus is active and assessed. Continue glucose monitoring and diabetes management.' @() @()),
  (New-Case 2 'case_02_diabetes_ckd_explicit' @($diabetes, $ckd1) 'Follow-up for type 2 diabetes mellitus and chronic kidney disease' 0 'Assessment: Type 2 diabetes mellitus with renal involvement. Chronic kidney disease stage 1 is related to diabetes. Plan: Continue diabetes management and monitor renal function.' @('diabetes -> CKD') @()),
  (New-Case 3 'case_03_diabetes_ckd_coexistence' @($diabetes, $ckd1) 'Follow-up for diabetes and kidney disease' 0 'Assessment: Type 2 diabetes mellitus and chronic kidney disease stage 1 are both present and reviewed. No causal relationship is documented.' @() @('diabetes -> CKD')),
  (New-Case 4 'case_04_diabetes_hypertension_explicit' @($diabetes, $hypertension) 'Evaluation of diabetes and blood pressure' 0 'Assessment: Type 2 diabetes mellitus with hypertension associated with diabetes. Plan: Continue diabetes management and monitor blood pressure.' @('diabetes -> hypertension') @()),
  (New-Case 5 'case_05_diabetes_hypertension_coexistence' @($diabetes, $hypertension) 'Chronic disease follow-up for diabetes' 0 'Assessment: Type 2 diabetes mellitus and essential hypertension are both assessed. No causal or associated relationship is documented.' @() @('diabetes -> hypertension')),
  (New-Case 6 'case_06_hypertension_single' @($hypertension) 'Evaluation of hypertension' 0 'Assessment: Essential hypertension is active. Plan: Continue blood pressure monitoring and treatment.' @() @()),
  (New-Case 7 'case_07_ckd_stage_three' @($ckd3) 'Follow-up for chronic kidney disease stage 3' 0 'Assessment: Chronic kidney disease stage 3 is active and its stage is confirmed. Plan: Monitor renal function.' @() @()),
  (New-Case 8 'case_08_hypertension_ckd_relationship' @($hypertension, $ckd3) 'Follow-up for hypertension and chronic kidney disease' 0 'Assessment: Hypertension is associated with chronic kidney disease stage 3. Renal function and blood pressure are monitored together.' @('hypertension -> CKD') @()),
  (New-Case 9 'case_09_diabetes_obesity' @($diabetes, $obesity) 'Follow-up for diabetes and obesity' 0 'Assessment: Type 2 diabetes mellitus is complicated by obesity. Plan: Continue diabetes management and weight intervention.' @('obesity -> diabetes management') @()),
  (New-Case 10 'case_10_diabetes_hyperlipidemia' @($diabetes, $hyperlipidemia) 'Follow-up for diabetes and lipid management' 0 'Assessment: Type 2 diabetes mellitus and hyperlipidemia are assessed. Lipid management is reviewed as cardiovascular risk reduction.' @() @()),
  (New-Case 11 'case_11_diabetes_ckd_hypertension' @($diabetes, $ckd1, $hypertension) 'Complex follow-up for diabetes, kidney disease, and hypertension' 0 'Assessment: Chronic kidney disease stage 1 is related to diabetes. Hypertension is present and reviewed without a documented causal relationship. Plan: Monitor renal function and blood pressure.' @('diabetes -> CKD') @('diabetes -> hypertension', 'hypertension -> CKD')),
  (New-Case 12 'case_12_copd_single' @($copd) 'Follow-up for chronic obstructive pulmonary disease' 0 'Assessment: Chronic obstructive lung disease is active. Plan: Continue inhaler therapy and monitor respiratory symptoms.' @() @()),
  (New-Case 13 'case_13_copd_hypertension' @($copd, $hypertension) 'Follow-up for COPD and hypertension' 0 'Assessment: Chronic obstructive lung disease and essential hypertension are both assessed. No direct relationship is documented.' @() @()),
  (New-Case 14 'case_14_asthma_single' @($asthma) 'Evaluation of asthma control' 0 'Assessment: Asthma is active and control is reviewed. Plan: Continue rescue and controller therapy as indicated.' @() @()),
  (New-Case 15 'case_15_asthma_rhinitis' @($asthma, $rhinitis) 'Follow-up for asthma and allergic rhinitis' 0 'Assessment: Allergic rhinitis contributes to asthma symptom burden. Plan: Treat rhinitis and continue asthma control therapy.' @('rhinitis -> asthma symptoms') @()),
  (New-Case 16 'case_16_heart_failure_single' @($heartFailure) 'Follow-up for heart failure' 0 'Assessment: Heart failure is active. Plan: Continue volume and symptom monitoring.' @() @()),
  (New-Case 17 'case_17_heart_failure_hypertension' @($heartFailure, $hypertension) 'Follow-up for heart failure and hypertension' 0 'Assessment: Hypertension contributes to heart failure management. Continue blood pressure and volume monitoring.' @('hypertension -> heart failure') @()),
  (New-Case 18 'case_18_obesity_hypertension_diabetes' @($obesity, $hypertension, $diabetes) 'Comprehensive follow-up for metabolic conditions' 2 'Assessment: Obesity contributes to diabetes and hypertension management. Hypertension is associated with diabetes. Plan: Address weight, glucose, and blood pressure together.' @('obesity -> diabetes', 'obesity -> hypertension', 'diabetes -> hypertension') @()),
  (New-Case 19 'case_19_hypothyroidism_single' @($hypothyroidism) 'Follow-up for hypothyroidism' 0 'Assessment: Hypothyroidism is active. Plan: Continue thyroid replacement and monitor laboratory response.' @() @()),
  (New-Case 20 'case_20_gerd_single' @($gerd) 'Evaluation of gastroesophageal reflux symptoms' 0 'Assessment: Gastroesophageal reflux disease is active. Plan: Continue reflux precautions and treatment.' @() @()),
  (New-Case 21 'case_21_osteoarthritis_single' @($osteoarthritis) 'Evaluation of knee pain from osteoarthritis' 0 'Assessment: Osteoarthritis of the knee is active and causing knee pain. Plan: Continue conservative joint management.' @() @()),
  (New-Case 22 'case_22_depression_single' @($depression) 'Follow-up for depressive disorder' 0 'Assessment: Depressive disorder is active and symptoms are reviewed. Plan: Continue behavioral health treatment.' @() @()),
  (New-Case 23 'case_23_acute_bronchitis' @($bronchitis) 'Evaluation of cough due to acute bronchitis' 0 'Assessment: Acute bronchitis explains the current cough. Plan: Supportive treatment and return precautions.' @() @()),
  (New-Case 24 'case_24_viral_respiratory_illness' @($viralUri) 'Evaluation of acute viral respiratory illness' 0 'Assessment: Upper respiratory infection is acute and viral in character. Plan: Supportive care and hydration.' @() @()),
  (New-Case 25 'case_25_dental_caries' @($dental) 'Evaluation of dental pain from dental caries' 0 'Assessment: Dental caries are the source of the current dental pain. Plan: Arrange definitive dental treatment.' @() @()),
  (New-Case 26 'case_26_acute_with_diabetes_history' @($bronchitis) 'Evaluation of acute bronchitis' 0 'Assessment: Acute bronchitis is the current reason for care. Historical type 2 diabetes mellitus is noted but is not assessed at this encounter.' @() @() 'ambulatory' @($diabetes) @($bronchitis)),
  (New-Case 27 'case_27_historical_diabetes_current_uri' @($viralUri) 'Evaluation of upper respiratory infection' 0 'Assessment: Upper respiratory infection is the current problem. Historical type 2 diabetes mellitus is not part of today''s assessment.' @() @() 'ambulatory' @($diabetes) @($viralUri)),
  (New-Case 28 'case_28_historical_multiple_current_htn' @($hypertension) 'Evaluation of hypertension' 0 'Assessment: Essential hypertension is the current problem. Historical diabetes and obesity are not assessed at this encounter.' @() @() 'ambulatory' @($diabetes, $obesity) @($hypertension)),
  (New-Case 29 'case_29_diabetes_ckd_anemia' @($diabetes, $ckd1, $anemia) 'Follow-up for diabetes, kidney disease, and anemia' 0 'Assessment: Chronic kidney disease stage 1 is related to diabetes. Anemia is also assessed, without a documented relationship to the other conditions.' @('diabetes -> CKD') @('anemia -> diabetes', 'anemia -> CKD')),
  (New-Case 30 'case_30_multiple_relationships' @($diabetes, $ckd1, $hypertension) 'Complex follow-up for diabetes, renal disease, and hypertension' 0 'Assessment: Chronic kidney disease stage 1 is related to diabetes, and hypertension is associated with diabetes. Plan: Monitor renal function and blood pressure as part of diabetes care.' @('diabetes -> CKD', 'diabetes -> hypertension') @('hypertension -> CKD'))
)

if ($OnlyCase) {
  $cases = @($cases | Where-Object { $_.CaseId -eq $OnlyCase })
  if ($cases.Count -ne 1) { throw "Unknown case: $OnlyCase" }
}

function New-ModuleDefinition($case) {
  $target = 'Target Encounter'
  $end = 'End Target Encounter'
  $procedure = 'Clinical Documentation'
  $complaint = 'Encounter Complaint'
  $firstCurrentState = 'Current Condition 1'
  $states = [ordered]@{
    Initial = [ordered]@{ type = 'Initial'; direct_transition = 'Delay Before Target' }
    'Delay Before Target' = [ordered]@{ type = 'Delay'; exact = [ordered]@{ quantity = 19; unit = 'years' }; direct_transition = if ($case.History.Count -gt 0) { 'Historical Condition 1' } else { $firstCurrentState } }
  }
  for ($historyIndex = 0; $historyIndex -lt $case.History.Count; $historyIndex++) {
    $condition = $case.History[$historyIndex]
    $number = $historyIndex + 1
    $stateName = "Historical Condition $number"
    $nextHistory = if ($number -lt $case.History.Count) { "Historical Condition $($number + 1)" } else { $firstCurrentState }
    $states[$stateName] = [ordered]@{ type = 'ConditionOnset'; target_encounter = "Historical Encounter $number"; codes = @([ordered]@{ system = 'SNOMED-CT'; code = $condition.Code; display = $condition.Display }); direct_transition = "Historical Encounter $number" }
    $states["Historical Encounter $number"] = [ordered]@{ type = 'Encounter'; encounter_class = 'ambulatory'; reason = $stateName; codes = @([ordered]@{ system = 'SNOMED-CT'; code = '390906007'; display = 'Follow-up encounter (procedure)' }); direct_transition = "End Historical Encounter $number" }
    $states["End Historical Encounter $number"] = [ordered]@{ type = 'EncounterEnd'; direct_transition = "Historical Delay $number" }
    $states["Historical Delay $number"] = [ordered]@{ type = 'Delay'; exact = [ordered]@{ quantity = 1; unit = 'years' }; direct_transition = $nextHistory }
  }
  for ($conditionIndex = 0; $conditionIndex -lt $case.Conditions.Count; $conditionIndex++) {
    $condition = $case.Conditions[$conditionIndex]
    $number = $conditionIndex + 1
    $stateName = "Current Condition $number"
    $next = if ($number -lt $case.Conditions.Count) { "Current Condition $($number + 1)" } else { $complaint }
    $states[$stateName] = [ordered]@{ type = 'ConditionOnset'; target_encounter = $target; codes = @([ordered]@{ system = 'SNOMED-CT'; code = $condition.Code; display = $condition.Display }); direct_transition = $next }
  }
  $states[$complaint] = [ordered]@{ type = 'Symptom'; symptom = $case.Complaint; range = [ordered]@{ low = 20; high = 20 }; direct_transition = $target }
  $reason = $case.Conditions[$case.ReasonIndex]
  $states[$target] = [ordered]@{ type = 'Encounter'; encounter_class = $case.EncounterClass; reason = $firstCurrentState; codes = @([ordered]@{ system = 'SNOMED-CT'; code = '390906007'; display = 'Follow-up encounter (procedure)' }); direct_transition = $procedure }
  $noteCode = "Clinical documentation: $($case.Note)"
  $states[$procedure] = [ordered]@{ type = 'Procedure'; reason = $firstCurrentState; note = $case.Note; codes = @([ordered]@{ system = 'SNOMED-CT'; code = '371530004'; display = $noteCode }); duration = [ordered]@{ low = 1; high = 1; unit = 'minutes' }; direct_transition = $end }
  $states[$end] = [ordered]@{ type = 'EncounterEnd'; direct_transition = 'Terminal' }
  $states.Terminal = [ordered]@{ type = 'Terminal' }
  return [ordered]@{ name = "$($case.CaseId) $($case.Slug) Module"; remarks = @('Generated by the native Generic Module Framework for clinical coding regression.'); states = $states }
}

function Invoke-SyntheaCase($case, $baseDirectory, $endDate) {
  $args = @('-p', '1', '-s', "$($case.Seed)", '-ps', "$($case.Seed)", '-cs', "$($case.ClinicianSeed)", '-r', '20100101', '-a', '25-25', '-E', $endDate, '-d', $moduleDir, '-m', "$($case.CaseId)*", "--exporter.baseDirectory=$baseDirectory")
  $groovy = '[' + (($args | ForEach-Object { "'" + $_.Replace('\', '\\').Replace("'", "\\'") + "'" }) -join ',') + ']'
  $oldErrorAction = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  & (Join-Path $repo 'gradlew.bat') run "-Params=$groovy" 2>$null | Out-Null
  $exitCode = $LASTEXITCODE
  $ErrorActionPreference = $oldErrorAction
  if ($exitCode -ne 0) { throw "Synthea failed for $($case.CaseId)" }
}

function Get-Bundle($baseDirectory) {
  $file = Get-ChildItem (Join-Path $baseDirectory 'fhir\*.json') | Where-Object { $_.Name -notmatch 'Information' } | Select-Object -First 1
  if ($null -eq $file) { throw "No patient FHIR found in $baseDirectory" }
  return Get-Content $file.FullName -Raw | ConvertFrom-Json
}

function Get-EncounterConditions($bundle, $encounter) {
  $ref = "urn:uuid:$($encounter.id)"
  return @($bundle.entry | Where-Object { $_.resource.resourceType -eq 'Condition' -and $_.resource.encounter.reference -eq $ref } | ForEach-Object { $_.resource })
}

function Get-TargetEncounter($bundle) {
  $matches = @()
  foreach ($entry in $bundle.entry) {
    if ($entry.resource.resourceType -ne 'Encounter') { continue }
    $encounter = $entry.resource
    $conditions = @(Get-EncounterConditions $bundle $encounter)
    if ($conditions.Count -gt 0 -and $encounter.period.start) { $matches += $encounter }
  }
  return $matches | Sort-Object { [datetime]$_.period.start } | Select-Object -Last 1
}

function Validate-Case($case, $bundle, $target) {
  $errors = New-Object System.Collections.Generic.List[string]
  $patients = @($bundle.entry | Where-Object { $_.resource.resourceType -eq 'Patient' })
  if ($patients.Count -ne 1) { $errors.Add('expected exactly one Patient') }
  $encounters = @($bundle.entry | Where-Object { $_.resource.resourceType -eq 'Encounter' } | ForEach-Object { $_.resource } | Sort-Object { [datetime]$_.period.start })
  if ($encounters.Count -eq 0) { $errors.Add('no Encounter resources') }
  if ($null -eq $target) { $errors.Add('no encounter-linked target found') }
  if ($null -ne $target) {
    $latest = $encounters[-1]
    if ($latest.id -ne $target.id) { $errors.Add('target is not latest Encounter') }
    if (-not $target.period.start -or -not $target.period.end) { $errors.Add('target period incomplete') }
    if ($target.class.code -ne 'AMB') { $errors.Add("target class is $($target.class.code), expected AMB") }
    if (-not $target.reasonCode -or $target.reasonCode.Count -eq 0) { $errors.Add('target has no Encounter.reasonCode') }
    $targetConditions = @(Get-EncounterConditions $bundle $target)
    if ($targetConditions.Count -lt 1) { $errors.Add('target has no linked Conditions') }
    foreach ($condition in $targetConditions) {
      if ($condition.code.coding[0].system -match 'ICD-10') { $errors.Add('Condition contains artificial ICD-10 code') }
    }
    $targetRef = "urn:uuid:$($target.id)"
    $reports = @($bundle.entry | Where-Object { $_.resource.resourceType -eq 'DiagnosticReport' -and $_.resource.encounter.reference -eq $targetRef } | ForEach-Object { $_.resource })
    $documents = @($bundle.entry | Where-Object { $_.resource.resourceType -eq 'DocumentReference' -and $_.resource.context.encounter.reference -eq $targetRef } | ForEach-Object { $_.resource })
    if ($reports.Count -eq 0) { $errors.Add('no DiagnosticReport linked to target') }
    if ($documents.Count -eq 0) { $errors.Add('no DocumentReference linked to target') }
    $note = ''
    $noteReport = @($reports | Where-Object { $_.presentedForm -and $_.presentedForm.Count -gt 0 -and $_.presentedForm[0].data } | Select-Object -First 1)
    if ($noteReport.Count -gt 0) { $note = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($noteReport[0].presentedForm[0].data)) }
    if (-not $note.ToLowerInvariant().Contains($case.Complaint.ToLowerInvariant())) { $errors.Add('clinical note lacks target complaint') }
    foreach ($condition in $case.CurrentConditions) {
      if (-not $note.ToLowerInvariant().Contains($condition.Display.ToLowerInvariant())) { $errors.Add("clinical note lacks $($condition.Display)") }
    }
    foreach ($relationship in $case.Relationships) {
      $relationshipParts = $relationship -split ' -> '
      $source = $relationshipParts[0].ToLowerInvariant()
      $target = $relationshipParts[1].ToLowerInvariant()
      $noteLower = $note.ToLowerInvariant()
      $sourceTerms = switch ($source) {
        'diabetes' { @('diabetes') }
        'obesity' { @('obesity', 'weight') }
        'hypertension' { @('hypertension', 'blood pressure') }
        'rhinitis' { @('rhinitis') }
        'anemia' { @('anemia') }
        default { @($source) }
      }
      $targetTerms = switch ($target) {
        'ckd' { @('chronic kidney disease', 'renal') }
        'diabetes' { @('diabetes') }
        'hypertension' { @('hypertension', 'blood pressure') }
        'asthma symptoms' { @('asthma') }
        'heart failure' { @('heart failure') }
        default { @($target -replace ' management', '') }
      }
      if ((@($sourceTerms | Where-Object { $noteLower.Contains($_) }).Count -eq 0) -or (@($targetTerms | Where-Object { $noteLower.Contains($_) }).Count -eq 0) -or ($noteLower -notmatch 'related|associated|contribut|complicat')) { $errors.Add("clinical note lacks relationship evidence: $relationship") }
    }
    foreach ($condition in $case.CurrentConditions) {
      $matching = @($targetConditions | Where-Object { $_.code.coding[0].code -eq $condition.Code })
      if ($matching.Count -eq 0) { $errors.Add("current condition not linked: $($condition.Display)") }
    }
  }
  [pscustomobject]@{ Valid = ($errors.Count -eq 0); Errors = @($errors) }
}

New-Item -ItemType Directory -Force $moduleDir | Out-Null
foreach ($case in $cases) {
  $module = New-ModuleDefinition $case | ConvertTo-Json -Depth 20
  Set-Content -Path (Join-Path $moduleDir "$($case.CaseId)_$($case.Slug).json") -Value $module -Encoding UTF8
}

$manifest = New-Object System.Collections.Generic.List[object]
$summary = New-Object System.Collections.Generic.List[string]
$summary.Add('# 30-case coding regression validation')
$summary.Add('')
$summary.Add('| Case | Conditions | Relationships | Latest encounter | Complaint | Valid |')
$summary.Add('| --- | --- | --- | --- | --- | --- |')

foreach ($case in $cases) {
  $caseDir = Join-Path $caseRoot $case.Slug
  $bootstrapDir = Join-Path $caseDir 'bootstrap'
  $finalDir = Join-Path $caseDir 'generated'
  Remove-Item -Recurse -Force $caseDir -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force $caseDir | Out-Null
  Invoke-SyntheaCase $case $bootstrapDir '20991231'
  $bootstrap = Get-Bundle $bootstrapDir
  $bootstrapTarget = Get-TargetEncounter $bootstrap
  if ($null -eq $bootstrapTarget) { throw "Unable to locate target for $($case.CaseId)" }
  $endDate = ([datetime]$bootstrapTarget.period.start).ToUniversalTime().AddDays(30).ToString('yyyyMMdd')
  Invoke-SyntheaCase $case $finalDir $endDate
  $bundle = Get-Bundle $finalDir
  $target = Get-TargetEncounter $bundle
  $validation = Validate-Case $case $bundle $target
  $targetConditions = if ($null -ne $target) { @(Get-EncounterConditions $bundle $target) } else { @() }
  $targetRef = if ($null -ne $target) { "urn:uuid:$($target.id)" } else { '' }
  $reports = @($bundle.entry | Where-Object { $_.resource.resourceType -eq 'DiagnosticReport' -and $_.resource.encounter.reference -eq $targetRef })
  $manifest.Add([ordered]@{
    case_id = $case.CaseId
    case_name = $case.Slug
    conditions = @($case.CurrentConditions | ForEach-Object { $_.Display })
    historical_conditions = @($case.History | ForEach-Object { $_.Display })
    intended_relationships = @($case.Relationships)
    intended_non_relationships = @($case.NonRelationships)
    encounter_setting = $case.EncounterClass
    target_encounter_id = if ($null -ne $target) { $target.id } else { '' }
    target_encounter_date = if ($null -ne $target) { $target.period.start } else { '' }
    target_encounter_type = if ($null -ne $target -and $target.type) { $target.type[0].coding[0].display } else { '' }
    target_encounter_reason = if ($null -ne $target -and $target.reasonCode) { $target.reasonCode[0].coding[0].display } else { '' }
    complaint = $case.Complaint
    seed = $case.Seed
    clinician_seed = $case.ClinicianSeed
    reference_date = '20100101'
    end_date = $endDate
    module_filename = "$($case.CaseId)_$($case.Slug).json"
    fhir_output_path = "regression_cases/$($case.Slug)/generated"
    validation_status = if ($validation.Valid) { 'PASS' } else { 'FAIL' }
    validation_errors = @($validation.Errors)
  })
  Set-Content -Path (Join-Path $caseDir 'case.json') -Value ($manifest[-1] | ConvertTo-Json -Depth 10) -Encoding UTF8
  Set-Content -Path (Join-Path $caseDir 'validation.json') -Value ($validation | ConvertTo-Json -Depth 10) -Encoding UTF8
  $conditionText = (($case.CurrentConditions | ForEach-Object { $_.Display }) -join '; ')
  $relationshipText = if ($case.Relationships.Count -gt 0) { $case.Relationships -join '; ' } else { 'none' }
  $latestText = if ($null -ne $target) { "$($target.period.start) / $($target.id)" } else { 'missing' }
  $summary.Add("| $($case.CaseId) | $conditionText | $relationshipText | $latestText | $($case.Complaint) | $($validation.Valid) |")
  if (-not $validation.Valid) { throw "$($case.CaseId) failed validation: $($validation.Errors -join '; ')" }
}

Set-Content -Path $manifestPath -Value ($manifest | ConvertTo-Json -Depth 20) -Encoding UTF8
Set-Content -Path $summaryPath -Value ($summary -join [Environment]::NewLine) -Encoding UTF8
Write-Output "Generated and validated $($cases.Count) cases."
