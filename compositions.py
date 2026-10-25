"""Seven deliberately art-directed newspaper compositions. IDs/data are immutable.
Each band contains independent vertical story stacks; no story heights or spacers.
"""
def S(index,role='standard',words=65,visual='none',**kw):return {'story':index,'role':role,'words':words,'visual':visual,**kw}
def G(widths,*columns,label=None):return {'widths':widths,'columns':[list(c) for c in columns],**({'label':label} if label else {})}
PLANS={
'home':[
 G([2,4,2],
   [S(0,'major',100),S(5,'rail',75,'bottom')],
   [S(8,'feature',75,'top'),G([1,1],[S(2,'brief',55)],[S(4,'brief',55)])],
   [S(1,'major',100),S(7,'rail',100)]),
 G([3,5],[S(3,'major',140)],[S(6,'major',95,'side')],label='Pesquisa & tecnologia')],
'pesquisa':[
 G([5,3],[S(0,'lead',110,'side'),S(1,'major',85)], [S(3,'major',120),S(6,'standard',100)]),
 G([2,3,3],[S(2,'compact',40),S(5,'compact',40),S(11,'compact',40)],[S(7,'standard',75),S(12,'brief',60),S(13,'brief',60)],[S(4,'standard',75),S(14,'brief',60),S(15,'brief',60)],label='Métodos, resultados e perguntas em aberto'),
 G([3,2,3],[S(8,'standard',80)],[S(10,'brief',60)],[S(9,'standard',80)],label='Populações & comportamento')],
'clinica':[
 G([3,3,2],[S(0,'lead',145,'bottom')],[S(1,'major',120),S(2,'standard',95)],[S(6,'rail',80),S(8,'rail',85)]),
 G([5,3],[G([1,1],[S(3,'standard',80),S(7,'brief',70)],[S(4,'standard',80),S(9,'brief',75)])],[S(5,'standard',95),S(10,'standard',90)],label='Decisão clínica • o contexto muda a conduta'),
 G([4,2,2],[S(11,'standard',75),S(12,'brief',60)],[S(13,'brief',125)],[S(14,'brief',40),S(15,'brief',40)],label='No consultório')],
'saude-publica':[
 G([3,5],[S(0,'lead',145,'bottom')],[S(1,'major',70,'middle'),G([1,1],[S(3,'brief',55,'top')],[S(2,'standard',90)])]),
 G([2,4,2],[S(5,'brief',35),S(7,'brief',35),S(9,'brief',35)],[G([1,1],[S(4,'standard',60),S(10,'brief',50)],[S(11,'standard',60),S(12,'brief',50)])],[S(6,'rail',80),S(8,'rail',80)],label='Saúde global • acesso, prevenção e continuidade'),
 G([3,2,3],[S(13,'standard',80)],[S(14,'brief',70)],[S(15,'standard',85)],label='Determinantes do cuidado')],
'formacao':[
 G([4,2,2],[S(0,'lead',140),S(14,'standard',105)],[S(1,'major',155,italic=True)],[S(11,'rail',60),S(12,'rail',65)]),
 G([5,3],[G([1,1,1],[S(2,'brief',45),S(3,'brief',45)],[S(4,'brief',45),S(5,'brief',45)],[S(7,'brief',45),S(15,'brief',45)])],[S(13,'major',110),S(10,'standard',110)],label='Ler, investigar, escrever • ferramentas de formação'),
 G([2,3,3],[S(6,'brief',70)],[S(8,'standard',85)],[S(9,'standard',85)],label='Responsabilidade científica')],
'inovacao':[
 G([2,6],[S(6,'rail',95),S(7,'rail',95)],[S(0,'lead',115,'side'),G([1,1],[S(1,'standard',90)],[S(2,'standard',90)])]),
 G([3,3,2],[S(3,'standard',85),S(4,'standard',80)],[S(5,'standard',80),S(8,'standard',80)],[S(9,'rail',55),S(10,'rail',55)],label='Da bancada à aplicação'),
 G([5,3],[G([1,1],[S(11,'brief',70)],[S(15,'brief',70)]),S(12,'major',120)],[S(13,'standard',75),S(14,'brief',65)],label='Dados, dispositivos e implementação')],
'instituicoes':[
 G([5,3],[S(0,'feature',60,'top'),G([1,1],[S(2,'brief',60)],[S(4,'brief',60)])],[S(5,'major',155),S(15,'standard',150)]),
 G([2,2,4],[S(1,'rail',75),S(3,'rail',75)],[S(6,'rail',75),S(7,'rail',75)],[G([1,1],[S(8,'standard',80),S(9,'brief',65)],[S(10,'standard',80),S(11,'brief',65)])],label='Elegibilidade • cada instituição tem suas regras'),
 G([2,3,3],[S(12,'brief',75)],[S(13,'standard',90)],[S(14,'standard',90)],label='Outras rotas de experiência internacional')]
}

def story_indices(node):
 if 'story' in node:return [node['story']]
 return [i for col in node['columns'] for child in col for i in story_indices(child)]
for key,plan in PLANS.items():
 indices=[i for node in plan for i in story_indices(node)]
 assert len(indices)==(9 if key=='home' else 16) and sorted(indices)==list(range(len(indices))),key
