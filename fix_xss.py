import os
import glob

escape_fn = """function escapeHTML(str) {
  if (typeof str !== 'string') str = String(str);
  return str.replace(/[&<>'"]/g, match => {
    switch(match) {
      case '&': return '&amp;';
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '"': return '&quot;';
      case "'": return '&#39;';
    }
  });
}
"""

def patch_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if "function escapeHTML" not in content:
        content = content.replace("const PERSONA_TYPES = [", escape_fn + "\nconst PERSONA_TYPES = [")
    
    # Escape in shock list
    content = content.replace("${s.label}", "${escapeHTML(s.label)}")
    content = content.replace("${s.effect}", "${escapeHTML(s.effect)}")
    
    # Escape in ranking list
    content = content.replace("${d.domain_id}", "${escapeHTML(d.domain_id)}")
    content = content.replace("${d.label || d.domain_id}", "${escapeHTML(d.label || d.domain_id)}")
    
    # Escape in legend
    content = content.replace("${pd.label}", "${escapeHTML(pd.label)}")
    
    # Escape in feed items - these have HTML embedded in them initially!
    # Instead of escaping item.text, we escape the variables before addFeedItem
    content = content.replace("${d.domain_id}</span>", "${escapeHTML(d.domain_id)}</span>")
    content = content.replace("${s.label}</span>", "${escapeHTML(s.label)}</span>")
    content = content.replace("${s.affects_domains.slice(0, 3).join(', ')}", "${escapeHTML(s.affects_domains.slice(0, 3).join(', '))}")
    
    # Tooltip escaping
    content = content.replace("${node.label}", "${escapeHTML(node.label)}")
    content = content.replace("${node.values.join(', ')}", "${escapeHTML(node.values.join(', '))}")
    content = content.replace("${node.pain_points.join(', ')}", "${escapeHTML(node.pain_points.join(', '))}")
    content = content.replace("${d.label}", "${escapeHTML(d.label)}")
    content = content.replace("${b.label}", "${escapeHTML(b.label)}")
    content = content.replace("${b.matched.join(', ')}", "${escapeHTML(b.matched.join(', '))}")
    content = content.replace("${d.domain_tags.join(', ')}", "${escapeHTML(d.domain_tags.join(', '))}")
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")

for f in glob.glob("viz/*.html"):
    patch_file(f)

for f in glob.glob("research/meta/*.html"):
    patch_file(f)

