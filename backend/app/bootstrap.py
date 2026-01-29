def include_routers(app):
    from app.modules.metadata_generator.router import router as metadata_router
    from app.modules.mapping.router import router as mapping_router
    from app.modules.Kg.router import router as kg_router
    from app.modules.nlp.router import router as nlp_router
    from app.modules.nlp_rag.router import router as nlp_rag_router

    app.include_router(metadata_router)
    app.include_router(mapping_router)
    app.include_router(kg_router)
    app.include_router(nlp_router)
    app.include_router(nlp_rag_router)
