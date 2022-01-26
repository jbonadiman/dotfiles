set nocompatible
filetype off

call plug#begin()

Plug 'edersonferreira/dalton-vim'
Plug 'ervandew/supertab'
Plug 'sheerun/vim-polyglot'
Plug 'preservim/nerdtree'
Plug 'vim-airline/vim-airline'
Plug 'dense-analysis/ale'
Plug 'gko/vim-coloresque'
Plug 'ryanoasis/vim-devicons'
Plug 'tiagofumo/vim-nerdtree-syntax-highlight'
Plug 'thaerkh/vim-indentguides'
Plug 'cohama/lexima.vim'
Plug 'neovim/nvim-lspconfig'

call plug#end()

" remaps
nnoremap <C-n> :NERDTreeToggle<CR>
nnoremap <F1> :bprevious<CR>
nnoremap <F2> :bnext<CR>
" end remaps

" lexima.vim settings
let g:indentguides_spacechar = '▏'
let g:indentguides_tabchar = '▏'
" end lexima.vim settings

" indentGuides settings
let g:indentguides_spacechar = '▏'
let g:indentguides_tabchar = '▏'
" end indentGuides settings

" airline settings
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#show_buffers = 1
let g:airline#extensions#tabline#switch_buffers_and_tabs = 1
let g:airline#extensions#tabline#tab_nr_type = 1
let g:airline_theme='dalton'
" end airline settings

" languages specifics
let g:rustfmt_autosave = 1
let g:python3_host_prog = '/usr/sbin/python3'
" end languages specifics

filetype plugin indent on " required
syntax enable

set number
set tabstop=2 shiftwidth=2 expandtab
hi MatchParen ctermbg=200 ctermfg=255

" shows carriage returns. To remove them, use: %s/Ctrl + VM/
" e ++ff=unix
