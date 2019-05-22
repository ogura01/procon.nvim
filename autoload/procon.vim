if exists('g:loaded_procon_nvim') | finish | endif
let g:loaded_procon_nvim = 1

let &runtimepath .= ',' . expand('<sfile>:h:h')

" ------------------------------------------------------------------------------
"  config
" ------------------------------------------------------------------------------
let s:procon_default_root_dir = $HOME . '/.procon'

" ------------------------------------------------------------------------------
"  function
" ------------------------------------------------------------------------------
function! procon#root_dir()
  if has_key(s:, 'procon_root_dir') | return s:procon_root_dir | endif
  return s:procon_default_root_dir
endfunction

function! procon#set_root_dir(dir)
  let! s:procon_root_dir = a:dir
  call ProUpdateRootDir()
endfunction

function! procon#update_contest_list()
  execute ProUpdateContestList
endfunction

function! procon#join_contest(contest_key)
  call ProJoinContest(a:contest_key)
endfunction

