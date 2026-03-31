#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/git-as.sh <team-member-number> "commit message"
# Team members:
#   1 - Tebti Mohamed Anis (IA / Tech Lead)
#   2 - Rais Walid (Backend)
#   3 - Aiche Youva (Frontend)
#   4 - Ceran Mohamed (ETL / Data)
#   5 - Chabla Yassine (DevOps)

if [ $# -lt 2 ]; then
    echo "Usage: $0 <1-5> \"commit message\""
    echo ""
    echo "  1 - Tebti Mohamed Anis (IA / Tech Lead)"
    echo "  2 - Rais Walid (Backend)"
    echo "  3 - Aiche Youva (Frontend)"
    echo "  4 - Ceran Mohamed (ETL / Data)"
    echo "  5 - Chabla Yassine (DevOps)"
    exit 1
fi

MEMBER=$1
shift
MESSAGE="$*"

case $MEMBER in
    1)
        NAME="Tebti Mohamed Anis"
        EMAIL="anis.tebti@democratia.dev"
        ;;
    2)
        NAME="Rais Walid"
        EMAIL="walid.rais@democratia.dev"
        ;;
    3)
        NAME="Aiche Youva"
        EMAIL="youva.aiche@democratia.dev"
        ;;
    4)
        NAME="Ceran Mohamed"
        EMAIL="mohamed.ceran@democratia.dev"
        ;;
    5)
        NAME="Chabla Yassine"
        EMAIL="yassine.chabla@democratia.dev"
        ;;
    *)
        echo "Error: member number must be between 1 and 5"
        exit 1
        ;;
esac

GIT_AUTHOR_NAME="$NAME" \
GIT_AUTHOR_EMAIL="$EMAIL" \
GIT_COMMITTER_NAME="$NAME" \
GIT_COMMITTER_EMAIL="$EMAIL" \
git commit -m "$MESSAGE"

echo "Committed as $NAME <$EMAIL>"
