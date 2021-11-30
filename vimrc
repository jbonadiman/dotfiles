set nocompatible
filetype off

set shellslash

let vundle_readme=expand('~/.vim/bundle/Vundle.vim/README.md')
if !filereadable(vundle_readme)
    echo "Installing Vundle.."
    echo ""
    silent !mkdir -p ~/.vim/bundle
    silent !git clone https://github.com/VundleVim/Vundle.vim ~/.vim/bundle/Vundle.vim
endif

set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
Plugin 'edersonferreira/dalton-vim'
Plugin 'ervandew/supertab'
Plugin 'sheerun/vim-polyglot'
Plugin 'preservim/nerdtree'
Plugin 'vim-airline/vim-airline'
Plugin 'dense-analysis/ale'
Plugin 'gko/vim-coloresque'
Plugin 'ryanoasis/vim-devicons'
Plugin 'tiagofumo/vim-nerdtree-syntax-highlight'
Plugin 'thaerkh/vim-indentguides'
Plugin 'cohama/lexima.vim'

call vundle#end()            " required

" Remaps
nnoremap <C-n> :NERDTreeToggle<CR>
nnoremap <F1> :bprevious<CR>
nnoremap <F2> :bnext<CR>
" Fim Remaps

" Configurações do lexima.vim
let g:indentguides_spacechar = '▏'
let g:indentguides_tabchar = '▏'
" Fim das configurações do lexima.vim'

" Configurações do Vim IndentGuides
let g:indentguides_spacechar = '▏'
let g:indentguides_tabchar = '▏'
" Fim das configurações do Vim IndentGuides

let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#show_buffers = 1
let g:airline#extensions#tabline#switch_buffers_and_tabs = 1
let g:airline#extensions#tabline#tab_nr_type = 1
let g:airline_theme='dalton'

filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line
syntax enable
let g:rustfmt_autosave = 1

set number
set tabstop=2 shiftwidth=2 expandtab
hi MatchParen ctermbg=200 ctermfg=255

" See carriage returns, to remove them, use: %s/Ctrl + VM/
" e ++ff=unix
