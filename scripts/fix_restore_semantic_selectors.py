"""
fix_restore_semantic_selectors.py

For entries where css_selector == css_selector_absolute (both became the full nth-of-type path),
reconstruct a semantic, human-readable css_selector and xpath:
  - css_selector: div#snapshot-N .class1 tag > :nth-child(N)
  - xpath: //div[@id='snapshot-N']//div[contains(@class,'...')]/tag[N]
The css_selector_absolute and xpath_absolute remain unchanged (full positional path).
"""

import json, os, re
from bs4 import BeautifulSoup

GOLD_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\gold\by_task\realestate'
SNAP_DIR = r'd:\PhD\myArticlesAndPapers\my-papers\5-WISE\wade-bench\data\raw_snapshots\realestate'


def get_classes(el):
    return ' '.join(el.get('class', []))


def semantic_selector_from_element(anchor_el, target_el):
    """
    Build a semantic CSS selector from anchor_el to target_el.
    Prefers class-based selectors over nth-of-type.
    Returns (css_selector, xpath) tuple.
    """
    if not anchor_el or not target_el:
        return None, None

    # Get path from target up to anchor
    path = []
    el = target_el
    while el and el != anchor_el:
        tag = el.name
        classes = el.get('class', [])
        el_id = el.get('id')

        if el_id:
            path.insert(0, ('#' + el_id, tag + "[@id='%s']" % el_id))
        elif classes:
            # Use the most specific/meaningful class
            meaningful = [c for c in classes if not re.match(r'^(w-|h-|p-|m-|text-|flex|grid|block|inline|hidden|relative|absolute|z-)', c)]
            if not meaningful:
                meaningful = classes[:1]
            cls = meaningful[0]
            # For li elements, also add :nth-child position
            siblings = el.find_previous_siblings(tag)
            nth = len(siblings) + 1
            if tag == 'li':
                if nth == 1:
                    path.insert(0, ('.%s:first-child' % cls if cls else ':first-child',
                                    'li[contains(@class,\'%s\')][1]' % cls if cls else 'li[1]'))
                else:
                    path.insert(0, ('li:nth-child(%d)' % nth,
                                    'li[%d]' % nth))
            else:
                path.insert(0, ('.%s' % cls,
                                "*[contains(@class,'%s')]" % cls))
        else:
            siblings = el.find_previous_siblings(tag)
            nth = len(siblings) + 1
            if tag == 'li':
                if nth == 1:
                    path.insert(0, ('li:first-child', 'li[1]'))
                else:
                    path.insert(0, ('li:nth-child(%d)' % nth, 'li[%d]' % nth))
            elif tag == 'ul':
                path.insert(0, ('ul', 'ul'))
            else:
                path.insert(0, (tag, tag))

        el = el.parent
        if el is None or el == anchor_el:
            break

    if not path:
        return None, None

    # Build anchor scope
    anchor_id = anchor_el.get('id')
    if anchor_id:
        css_anchor = '%s#%s' % (anchor_el.name, anchor_id)
        xpath_anchor = "//%s[@id='%s']" % (anchor_el.name, anchor_id)
    else:
        return None, None

    # CSS: space-separated (descendant) for classes, > for li
    css_parts = []
    for css_part, _ in path:
        css_parts.append(css_part)

    css_sel = css_anchor + ' ' + ' '.join(css_parts)

    # XPath: // for class ancestors, / for positional
    xpath_parts = []
    for _, xp_part in path:
        xpath_parts.append(xp_part)

    xpath = xpath_anchor + '//' + '/'.join(xpath_parts)

    return css_sel, xpath


def count_matches(soup, sel):
    try:
        return len(soup.select(sel))
    except Exception:
        return -1


files = sorted([f for f in os.listdir(GOLD_DIR) if f.endswith('.json')])

for fname in files:
    fpath = os.path.join(GOLD_DIR, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    snap_id = data.get('snapshot_id', '')
    html_path = os.path.join(SNAP_DIR, snap_id, 'page.html')
    if not os.path.exists(html_path):
        continue

    soup = None
    changes = 0

    for rec in data.get('records', []):
        prov = rec.get('provenance', {})

        for field_name, pv in prov.items():
            if not isinstance(pv, dict): continue

            css = pv.get('css_selector', '')
            css_abs = pv.get('css_selector_absolute', '')
            xpath = pv.get('xpath', '')
            xpath_abs = pv.get('xpath_absolute', '')

            # Only fix entries where css_selector == css_selector_absolute
            # (both are full nth-of-type paths) OR xpath == xpath_absolute
            css_same = css and css_abs and css == css_abs
            xpath_same = xpath and xpath_abs and xpath == xpath_abs

            if not css_same and not xpath_same:
                continue

            if soup is None:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

            # Find the target element using css_selector_absolute
            try:
                elements = soup.select(css_abs)
            except Exception:
                continue

            if not elements or len(elements) != 1:
                continue

            target_el = elements[0]

            # Find the anchor (div#snapshot-N) in target's ancestors
            anchor_el = None
            parent = target_el.parent
            while parent:
                if parent.get('id') and re.match(r'snapshot-\d+', parent.get('id', '')):
                    anchor_el = parent
                    break
                parent = parent.parent

            if not anchor_el:
                # Try #__next or main or any ID ancestor
                parent = target_el.parent
                while parent:
                    if parent.get('id'):
                        anchor_el = parent
                        break
                    parent = parent.parent

            if not anchor_el:
                continue

            new_css, new_xpath = semantic_selector_from_element(anchor_el, target_el)

            if new_css and css_same:
                # Verify uniqueness
                n = count_matches(soup, new_css)
                if n == 1:
                    pv['css_selector'] = new_css
                    changes += 1

            if new_xpath and xpath_same:
                pv['xpath'] = new_xpath
                changes += 1

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if changes > 0:
        print('%-60s  semantic=%d' % (fname, changes))

print('\nDone.')
