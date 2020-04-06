#!/bin/bash
# run daily to update covid stats

jupyter nbconvert --to html --execute curvefit-global.ipynb  --output ./curvefit-global.html
jupyter nbconvert --to html --execute curvefit-us.ipynb --output ./curvefit-us.html

#git add *
#git commit -m 'automatic update'
#git push