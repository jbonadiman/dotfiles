set number

set relativenumber
set autoindent
set tabstop=2
set softtabstop=2
set shiftwidth=2
set smarttab
set expandtab
set mouse=a

call plug#begin()

Plug 'tpope/vim-surround' " Surround with ysw
Plug 'vim-airline/vim-airline'
Plug 'ap/vim-css-color'
Plug 'tpope/vim-commentary'
Plug 'edersonferreira/dalton-vim'
Plug 'preservim/nerdtree'
Plug 'ryanoasis/vim-devicons'
Plug 'tiagofumo/vim-nerdtree-syntax-highlight'
Plug 'thaerkh/vim-indentguides'
Plug 'preservim/tagbar'
Plug 'neoclide/coc.nvim'

call plug#end()

" remaps
nnoremap <C-n> :NERDTreeToggle<CR>
nnoremap <F1> :bprevious<CR>
nnoremap <F2> :bnext<CR>
nnoremap <F8> :TagbarToggle<CR>
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

hi MatchParen ctermbg=200 ctermfg=255

" shows carriage returns. To remove them, use: %s/Ctrl + VM/
" e ++ff=unix
