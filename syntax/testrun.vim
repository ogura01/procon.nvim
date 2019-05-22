" ------------------------------------------------------------------------------
"  syntax
" ------------------------------------------------------------------------------
syntax keyword testrunAC AC
syntax keyword testrunWA WA
syntax keyword testrunTLE TLE
" syntax match testrunSampleCase /SampleCase([^)]*)/
syntax match testrunEqualLine /====[=]*/
syntax match testrunNormalLine /----[-]*/

highlight link testrunAC Statement
highlight link testrunWA DiffDelete
highlight link testrunTLE Search
highlight link testrunEqualLine Comment
highlight link testrunNormalLine Comment
