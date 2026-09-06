def cart_context(request):
    count = 0
    if request.user.is_authenticated and hasattr(request.user, "client"):
        panier = request.user.client.paniers.filter(actif=True).prefetch_related("lignes").first()
        if panier:
            count = panier.nombre_articles
    return {"cart_count": count}

