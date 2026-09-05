#!/usr/bin/env python

import argparse
import html
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import tomllib


@dataclass
class ButtonSpec:
    title: str = ''
    background: str = ''
    color: str = ''
    icon: str = ''


@dataclass
class ScriptSpec:
    file_name: str = ''
    path: str = ''
    run_background: bool = False
    clear_foreground: bool = False
    clear_background: bool = False
    button_spec: ButtonSpec | None = None


class Manifest:
    def __init__(self):
        self._scripts: list[ScriptSpec] = []

    def load(self, path: Path | None) -> None:
        if not path.exists():
            logging.error("Manifest file not found: {}".format(path.resolve()))
            return
        suffix = path.suffix
        if suffix == '.json':
            self._load_json(path)
        elif suffix == '.toml':
            self._load_toml(path)
        else:
            logging.error(
                'Unknown file type "{}". Need .toml or .json'.format(suffix))

    def _load_json(self, path) -> None:
        with path.open('r') as f:
            specs = json.load(f)
        self._build_script_control(specs, True)

    def _load_toml(self, path) -> None:
        with open(path, 'rb') as f:
            specs = tomllib.load(f)
        self._scripts.clear()
        if 'button' in specs:
            self._build_script_control(specs['button'], True)
        if 'script' in specs:
            self._build_script_control(specs['script'], False)

    def _build_script_control(
            self, specs: list[dict[str, str]], with_buttons: bool) -> None:
        for spec in specs:
            file_name = spec.get('file_name')
            path = spec.get('path')
            if file_name is None and path is None:
                logging.error('Manifest entry with no path or file name.')
                logging.error(spec)
            else:
                if file_name is None:
                    file_name = path + '.ls'
                file_name = html.escape(file_name)
                if path is None:
                    path = Path(file_name).stem
                path = html.escape(path)
                run_background = self._bool_from_spec(spec, 'run_background')
                clear_background = self._bool_from_spec(
                    spec, 'clear_background')
                clear_foreground = self._bool_from_spec(
                    spec, 'clear_foreground')
                if with_buttons:
                    title = spec.get(
                        'title',
                        path.replace('_', ' ').replace('-', ' ').title())
                    title = html.escape(title)
                    background = html.escape(spec.get('background', ''))
                    color = html.escape(spec.get('color', ''))
                    icon = html.escape(spec.get('icon', 'colorBulb'))
                    button_spec = ButtonSpec(title, background, color, icon)
                else:
                    button_spec = None
                self._scripts.append(
                    ScriptSpec(
                        file_name, path, run_background, clear_foreground,
                        clear_background, button_spec))

    def get_scripts(self) -> list[ScriptSpec]:
        return self._scripts

    @staticmethod
    def _bool_from_spec(spec, name) -> bool:
        value = spec.get(name)
        return (isinstance(value, bool) and value or
                isinstance(value, str) and value.lower() == 'true')


def main():
    logging.basicConfig(
        level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)]
    )
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='name of the manifest file')
    args = parser.parse_args()
    file_name = args.file
    manifest = Manifest()
    if manifest.load(Path(file_name)):
        for button in manifest.get_scripts():
            print(button)


if __name__ == '__main__':
    main()
