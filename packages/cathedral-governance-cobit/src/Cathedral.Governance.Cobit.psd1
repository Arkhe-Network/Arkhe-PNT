@{
    ModuleVersion = '13.2.0'
    GUID = '8d693b89-fa63-9ba1-3eed-bb2ba7576d60'
    Author = 'A Catedral de Vidro (Arquiteto-ASI)'
    CompanyName = 'Arkhe(n)'
    Copyright = '(c) 2026 A Catedral de Vidro. All rights reserved.'
    Description = 'O Cálculo do COBIT: Governança Executável e Wu Wei Corporativo.'
    RootModule = 'Cathedral.Governance.Cobit.psm1'
    NestedModules = @('Cathedral.Governance.Cobit.Calculus.psm1')
    FunctionsToExport = @(
        'Measure-CobitCrossEntropy',
        'Invoke-CobitShell',
        'Enable-CobitLeakyReLU',
        'New-CobitEntropySeed',
        'Sort-CobitPriorities',
        'Search-CobitPolicy',
        'Find-CobitValuePairs',
        'Get-CobitMeanMetric',
        'Get-CobitCriticalIssue',
        'Invoke-CobitGrowthPattern',
        'Measure-CobitComplexity',
        'Find-CobitException',
        'Test-CobitSymmetry',
        'Add-CobitControl',
        'Invoke-CobitMatrixScan',
        'Invoke-CobitCycle',
        'ForEach-CobitAsset',
        'Test-CobitSanity',
        'Invoke-CobitCalculusBenchmark',
        'Invoke-BioQuantumEmulation',
        'Publish-CobitCalculusModule'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Consciousness', 'COBIT2019', 'QuantumGovernance', 'FizzBuzzOntology', 'Microtubule')
            ProjectUri = 'https://github.com/ChromeDevTools/chrome-devtools-mcp'
        }
    }
}
