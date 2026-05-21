# SimpleMemAdapter(db_dir, clear=False) wrapping SimpleMemSystem with add_turn(speaker, content, ts), finalize(), ask(query)

class SimpleMemSystem:
    def __init__(self, db_dir, clear=False):
        self.db_dir = db_dir
        self.clear = clear
        self.turns = []

    def add_turn(self, speaker, content, ts=None):
        self.turns.append((speaker, content, ts))

    def finalize(self):
        # Here you would save the turns to the database or perform any final processing
        pass

    def ask(self, query):
        # Here you would implement the logic to answer the query based on the stored turns
        return "This is a placeholder response to the query: " + query


class SimpleMemAdapter:
    def __init__(self, db_dir, clear=False):
        self.mem_system = SimpleMemSystem(db_dir, clear)

    def add_turn(self, speaker, content, ts=None):
        self.mem_system.add_turn(speaker, content, ts)

    def finalize(self):
        self.mem_system.finalize()

    def ask(self, query):
        return self.mem_system.ask(query)


