echo "# tip.training" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/herrkrueger/tip.ing.git
git push -u origin main
git init
git remote add origin https://github.com/herrkrueger/tip.training.git
git push -u origin main
git branch -M main
git push -u origin main
