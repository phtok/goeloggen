#!/bin/bash
# Goetheanum-Schriften: Mac-Paket bauen (auf macOS, pkgbuild/productbuild).
#
#   bash tools/schrift-installer/mac/build.sh [Fassung] [Ausgabeordner]
#
# Bringt die Schriften aus dem Repo-Stand mit; installiert wird über
# assets/fonts/goetheanum/Installer/mac.sh (--alle --quelle). Unsigniert.
# Gebaut von .github/workflows/schrift-installer.yml.
set -euo pipefail

FASSUNG="${1:-2.9}"
HIER="$(cd "$(dirname "$0")" && pwd)"
WURZEL="$HIER/../../../assets/fonts/goetheanum"
AUS="${2:-$HIER/../../../dist}"
BAU="$(mktemp -d)"
trap 'rm -rf "$BAU"' EXIT
mkdir -p "$AUS" "$BAU/pkgs"

paket() { # $1 = Kennung (Endung), $2 = Skriptordner
  local name="${1:-schriften}"
  local kennung="ch.goetheanum.schriften${1:+.$1}"
  pkgbuild --nopayload --scripts "$2" --identifier "$kennung" \
    --version "$FASSUNG" "$BAU/pkgs/$name.pkg"
}

# Vorbereiten: Marken eines abgebrochenen Laufs entfernen
mkdir -p "$BAU/vorbereiten"
cat > "$BAU/vorbereiten/postinstall" <<'SKRIPT'
#!/bin/bash
rm -rf /private/var/root/.goetheanum-schriften
SKRIPT

# Zusätze: je eine Marke im Ordner von root
for zusatz in kyrillisch arabisch variabel; do
  mkdir -p "$BAU/$zusatz"
  cat > "$BAU/$zusatz/postinstall" <<SKRIPT
#!/bin/bash
install -d -m 700 /private/var/root/.goetheanum-schriften
touch /private/var/root/.goetheanum-schriften/$zusatz
SKRIPT
done

# Hauptpaket: Schriften und mac.sh neben dem Abschluss-Skript
H="$BAU/schriften"
mkdir -p "$H/Office" "$H/Begleitschriften" "$H/Variable"
cp "$WURZEL"/Office/*.ttf "$H/Office/"
cp "$WURZEL"/Begleitschriften/*.ttf "$H/Begleitschriften/"
cp "$WURZEL/Variable/Goetheanum-Variabel-v$FASSUNG.otf" "$H/Variable/"
cp "$WURZEL/Installer/mac.sh" "$H/mac.sh"
cp "$HIER/postinstall" "$H/postinstall"

chmod 755 "$BAU"/*/postinstall "$H/mac.sh"
paket vorbereiten "$BAU/vorbereiten"
for zusatz in kyrillisch arabisch variabel; do paket "$zusatz" "$BAU/$zusatz"; done
paket "" "$H"

sed "s/@FASSUNG@/$FASSUNG/g" "$HIER/distribution.xml" > "$BAU/distribution.xml"
productbuild --distribution "$BAU/distribution.xml" --package-path "$BAU/pkgs" \
  "$AUS/Goetheanum-Schriften-$FASSUNG-Mac.pkg"
echo "gebaut: $AUS/Goetheanum-Schriften-$FASSUNG-Mac.pkg"
