# Architecture considerations

A few notes on *why* the project is built the way it is. Most of them are my deliberate choices, albeit unusual.

## Project structure

The project uses a classic Python package format, with the outer folder containing:

- `instance/` with `config.py` kept outside of git (I chose not to use env vars here to understand where it would be better WITH them)
- `tests/`
- `uploads/images/`

The inner project is separated into `models` / `views` / `templates`, following the MVT model.

## Database setup

I chose to start from a pre-existing `users` table that I reflect, then create the other tables normally. This taught me a lot about the Flask init flow. I believe using Alembic right away would have taken away from the problems I encountered and solved.

## Separation of concerns (lacking)

As this is my first larger Python project, I went with a *"refactor when it feels clunky"* approach. At first all the logic sat in the routes, and when they got too heavy I moved the suitable pieces into the model. This is also why I used a separate file per model — to keep things clean and organized.

**Improvement opportunity:** by the time I reached the travel/place edit pages, the route logic felt too complicated even after moving everything db-related into the model. Refactoring the business logic into a *Service layer* (new to me) was on my list, but there were no other routes this heavy, so I decided to leave it as is for this project.

## Templates

The templates are structured to mirror the views, with a separate `snippets/` section for reusable pieces.

## Overall

Overall I feel excellent about how Web Travel Journal turned out. The choices were intentional, I learned a lot by doing things the manual way first and refactoring incrementally, and I have a clear idea of what I need to improve next.
