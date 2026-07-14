from mcp.server.fastmcp import FastMCP
from db_atomic import get_db_connection, init_db
import uuid

# Initialize the MCP Server
mcp = FastMCP("cortex-milestones")

# Ensure DB is initialized
init_db()

def _check_dependencies_bft(conn, milestone_id: str) -> bool:
    """Check if all parent dependencies are BFT_Frozen."""
    cursor = conn.execute('''
        SELECT m.status 
        FROM edges e
        JOIN milestones m ON e.parent_id = m.id
        WHERE e.child_id = ?
    ''', (milestone_id,))
    
    parents = cursor.fetchall()
    for parent in parents:
        if parent['status'] != 'BFT_Frozen':
            return False
    return True

@mcp.tool()
def add_milestone(title: str, description: str, dependencies: list[str] = None) -> str:
    """Add a new milestone to the Ouroboros DAG. dependencies is a list of parent milestone IDs."""
    milestone_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        # Initial status is Pending.
        conn.execute(
            'INSERT INTO milestones (id, title, description, status) VALUES (?, ?, ?, ?)',
            (milestone_id, title, description, 'Pending')
        )
        
        if dependencies:
            for parent_id in dependencies:
                # Ensure parent exists
                parent = conn.execute('SELECT id FROM milestones WHERE id = ?', (parent_id,)).fetchone()
                if not parent:
                    raise ValueError(f"Parent milestone {parent_id} does not exist.")
                    
                conn.execute(
                    'INSERT INTO edges (parent_id, child_id) VALUES (?, ?)',
                    (parent_id, milestone_id)
                )
        
        # Check if it can transition to Active
        if _check_dependencies_bft(conn, milestone_id):
            conn.execute('UPDATE milestones SET status = ? WHERE id = ?', ('Active', milestone_id))
            status = 'Active'
        else:
            status = 'Pending'
            
    return f"Milestone '{title}' created with ID: {milestone_id} (Status: {status})"

@mcp.tool()
def resolve_milestone(milestone_id: str, bft_hash: str) -> str:
    """Mark a milestone as BFT_Frozen with its Git BFT hash and update its children."""
    with get_db_connection() as conn:
        milestone = conn.execute('SELECT status FROM milestones WHERE id = ?', (milestone_id,)).fetchone()
        if not milestone:
            return f"Error: Milestone {milestone_id} not found."
            
        if milestone['status'] == 'BFT_Frozen':
            return f"Milestone {milestone_id} is already frozen."
            
        if milestone['status'] == 'Pending':
            return f"Error: Milestone {milestone_id} is Pending. Cannot resolve until dependencies are met."

        # Freeze it
        conn.execute(
            'UPDATE milestones SET status = ?, bft_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            ('BFT_Frozen', bft_hash, milestone_id)
        )
        
        # Check children to see if they can transition to Active
        children_cursor = conn.execute('SELECT child_id FROM edges WHERE parent_id = ?', (milestone_id,))
        children = [row['child_id'] for row in children_cursor.fetchall()]
        
        activated = []
        for child_id in children:
            if _check_dependencies_bft(conn, child_id):
                conn.execute('UPDATE milestones SET status = ? WHERE id = ?', ('Active', child_id))
                activated.append(child_id)
                
    result = f"Milestone {milestone_id} resolved with BFT hash {bft_hash}."
    if activated:
        result += f"\nActivated children: {', '.join(activated)}"
    return result

@mcp.tool()
def get_milestone_graph() -> str:
    """Return a representation of all milestones and their dependencies."""
    output = []
    with get_db_connection() as conn:
        milestones = conn.execute('SELECT id, title, status, bft_hash FROM milestones').fetchall()
        for m in milestones:
            output.append(f"[{m['status']}] {m['title']} (ID: {m['id']}) - Hash: {m['bft_hash'] or 'None'}")
            
            parents = conn.execute('SELECT parent_id FROM edges WHERE child_id = ?', (m['id'],)).fetchall()
            if parents:
                parent_ids = [p['parent_id'] for p in parents]
                output.append(f"    Dependencies: {', '.join(parent_ids)}")
    
    if not output:
        return "Graph is empty."
    return "\\n".join(output)

if __name__ == "__main__":
    mcp.run(transport='stdio')
