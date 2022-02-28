set -e
INSTALL_DIR=~
EXPORT_LINE="export PATH=\"$INSTALL_DIR/dema_engine_macos:\$PATH\" #DEMATRADING.AI"


add_to_bash_profile() {
    echo "Adding engine shortcut to .bash_profile"
   
    if grep -q "#DEMATRADING.AI" ~/.bash_profile; then
         sed -i -e "s/.*#DEMATRADING.AI*/$(echo $EXPORT_LINE | sed "s=/=\\\/=g"
)/" ~/.bash_profile
    else
        echo "$EXPORT_LINE" >> ~/.bash_profile
    fi
}

add_to_zsh_profile() {
    echo "Adding engine shortcut to .zsh_profile"
    
    if grep -q "#DEMATRADING.AI" ~/.zshrc ; then
         sed -i -e "s/.*#DEMATRADING.AI*/$(echo $EXPORT_LINE | sed "s=/=\\\/=g"
)/" ~/.zshrc
    else
        echo "$EXPORT_LINE" >> ~/.zshrc
    fi
}


if [ ! -d "$INSTALL_DIR/dema_engine_macos" ]; then
    mkdir $INSTALL_DIR/dema_engine_macos
fi 


cd $INSTALL_DIR
(cd $INSTALL_DIR && curl -O --url "https://engine-store.ams3.digitaloceanspaces.com/engine-macos-test_executable.zip")
unzip -q -o $INSTALL_DIR/engine-macos-test_executable.zip -d $INSTALL_DIR/dema_engine_macos

rm $INSTALL_DIR/engine-macos-test_executable.zip

echo "installing..."
$INSTALL_DIR/dema_engine_macos/engine &> /dev/null || true

case $SHELL in
  "/bin/bash")
    # echo "Bash is used."
    add_to_bash_profile
    ;;

  "/bin/zsh")
    # echo "Zsh is used."
    add_to_zsh_profile
    ;;
esac

echo ""
echo " 'engine' installed"
echo ""

echo "Open a new Terminal and run 'engine init NEW_DIRECTORY_NAME' to get started. "