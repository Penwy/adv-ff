#!/usr/bin/env bash

cd "$(dirname "$0")" || {
    echo "Cannot access $(dirname "$0")" >&2
    exit 1
}

declare repo_name=adv-ff \
    repo=repo \
    manifest=com.obsproject.Studio.Plugin.adv-ff.json \
    python_requirements=requirements.txt \
    bundle_name=com.obsproject.Studio.Plugin.adv-ff.flatpak

declare exe missing_exe
for exe in flatpak-builder flatpak_pip_generator jq; do
    command -v "$exe" >/dev/null 2>&1 || {
        echo "Missing $exe" >&2
        missing_exe=1
    }
done
[ "$missing_exe" ] && exit 2
unset exe missing_exe

if [ ! -r "$manifest" ]; then
    echo "manifest $manifest is missing or unreadable"
    exit 3
fi

declare app_id sdk branch
if ! {
    app_id=$(jq -r '.id' "$manifest") &&
    sdk=$(jq -r '.sdk' "$manifest") &&
    branch=$(jq -r '.branch' "$manifest")
}; then
    echo "Error occurred when reading $manifest"
    exit 4
fi

flatpak_pip_generator --runtime "$sdk" -r "$python_requirements"

if ! {
    flatpak-builder --force-clean --install-deps-from=flathub --repo="$repo" _build "$manifest" &&
    flatpak build-bundle --runtime "$repo" "$bundle_name" "$app_id" "$branch"
}; then
    exit $?
fi

printf -- '\n%s\n' "Do you want to install $app_id?: (y/N)"
declare line
read -r line
[ ! "${line@L}" = y ] && exit 0
unset line

flatpak --user install "$bundle_name"
