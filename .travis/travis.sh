if [ -z ${DEPLOY_KEY+x} ]; then 
    echo "DEPLOY_KEY is unset";
    echo "if you want to automatically deploy on you GH Pages"
    echo "Generate a pair of key for youfork/pep, base64 encode it"
    echo "and set is as a private ENV variable on travis named DEPLOY_KEY"
else 
    if [[ $TRAVIS_PULL_REQUEST == false
          && $TRAVIS_REPO_SLUG != 'python/peps'
          && $TRAVIS_BRANCH != 'master'
          && $TRAVIS_BRANCH != 'gh-pages' ]]; 
      then
        echo "DEPLOY_KEY is set";
        echo "unpacking private ssh_key";
        echo $DEPLOY_KEY | base64 -d > ~/.ssh/github_deploy ;
        echo -e "Host github.com\n\tHostName github.com\n\tUser git\n\tIdentityFile ~/.ssh/github_deploy\n" >> ~/.ssh/config
        chmod 600 ~/.ssh/github_deploy
        eval `ssh-agent -s`
        ssh-add ~/.ssh/github_deploy
        ORIGIN="ssh://github.com/$TRAVIS_REPO_SLUG"
        git clone $ORIGIN deploy
        echo 'cd deploy'
        cd deploy
        echo '==== pwd ==='
        pwd

        echo '=== configuring git for push ==='

        git config --global user.email "travis-ci@travis.ci"
        git config --global user.name "TravisCI"
        git checkout -b gh-pages
        git config --global push.default simple
        git reset --hard origin/gh-pages
        
        mkdir -p $TRAVIS_BRANCH

        cp -v $HOME/build/$TRAVIS_REPO_SLUG/*.html $TRAVIS_BRANCH
        cp -v $HOME/build/$TRAVIS_REPO_SLUG/*.css $TRAVIS_BRANCH

        echo '===== git add .  ===='
        git add $TRAVIS_BRANCH
        
        echo '===== git status  ===='
        git status

        git commit -am"deploy of branch $BRANCH"
        git push origin gh-pages:gh-pages

        echo '==========================='
        echo $(echo $TRAVIS_REPO_SLUG | sed -e 's/\//.github.io\//')"/$TRAVIS_BRANCH/pep-0000.html"
        echo '==========================='
    fi 
fi
