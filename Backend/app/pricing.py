# backend/app/pricing.py
def compute_pricing(matches):
    # simple pricing: base_price * 1.2 margin
    line_items = []
    total = 0.0
    for m in matches:
        base = m.get("price_base", 100.0)
        qty = m.get("quantity", 1)
        amount = base * qty
        line_items.append({"sku": m.get("sku_code"), "qty": qty, "amount": amount})
        total += amount
    margin = total * 0.10
    total_with_margin = total + margin
    return {"line_items": line_items, "total": total_with_margin, "margin": margin}
