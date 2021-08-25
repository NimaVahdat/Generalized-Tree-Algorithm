class Node(object):
    def __init__(self):
        self.suffix_node = -1  
        self.child = []
        self.parent = None
        self.descendant = 0
        self.d = 0
        self.suffix_index = -1


class Edge(object):
    def __init__(self, f_char, l_char, source_node_index, dest_node_index):
        self.f_char = f_char
        self.l_char = l_char
        self.source_node_index = source_node_index
        self.dest_node_index = dest_node_index

    @property
    def length(self):
        return self.l_char - self.f_char


class Suffix(object):
    def __init__(self, source_node_index, f_char, l_char):
        self.source_node_index = source_node_index
        self.f_char = f_char
        self.l_char = l_char
        
    @property
    def length(self):
        return self.l_char - self.f_char
                
    def explicit(self):
        return self.f_char > self.l_char

        
class SuffixTree(object):
    def __init__(self, string, case_insensitive=False):
        self.string = string
        self.case_insensitive = case_insensitive
        self.N = len(string) - 1
        self.nodes = [Node()]
        self.edges = {}
        self.active = Suffix(0, 0, -1)
        if self.case_insensitive:
            self.string = self.string.lower()
        self.strings_num = 1
        self.strings_pos = [0]
        for i in range(len(string)):
            if self.string[i] == '>':
                self.strings_num += 1
                self.strings_pos.append(i+1)
            self._add_prefix(i)
        self.repair()
           
    def _add_prefix(self, l_char):
        last_parent_node = -1
        while True:
            parent_node = self.active.source_node_index
            if self.active.explicit():
                if (self.active.source_node_index, self.string[l_char]) in self.edges:
                    break
            else:
                e = self.edges[self.active.source_node_index, self.string[self.active.f_char]]
                if self.string[e.f_char + self.active.length + 1] == self.string[l_char]:
                    break
                parent_node = self._split_edge(e, self.active)
        

            self.nodes.append(Node())
            e = Edge(l_char, self.N, parent_node, len(self.nodes) - 1)
            self._insert_edge(e)
            
            if last_parent_node > 0:
                self.nodes[last_parent_node].suffix_node = parent_node
            last_parent_node = parent_node
            
            if self.active.source_node_index == 0:
                self.active.f_char += 1
            else:
                self.active.source_node_index = self.nodes[self.active.source_node_index].suffix_node
            self._canonize_suffix(self.active)
        if last_parent_node > 0:
            self.nodes[last_parent_node].suffix_node = parent_node
        self.active.l_char += 1
        self._canonize_suffix(self.active)
        
    def _insert_edge(self, edge):
        self.edges[(edge.source_node_index, self.string[edge.f_char])] = edge
        
    def _remove_edge(self, edge):
        self.edges.pop((edge.source_node_index, self.string[edge.f_char]))
        
    def _split_edge(self, edge, suffix):
        self.nodes.append(Node())
        e = Edge(edge.f_char, edge.f_char + suffix.length, suffix.source_node_index, len(self.nodes) - 1)
        self._remove_edge(edge)
        self._insert_edge(e)
        self.nodes[e.dest_node_index].suffix_node = suffix.source_node_index
        edge.f_char += suffix.length + 1
        edge.source_node_index = e.dest_node_index
        self._insert_edge(edge)
        return e.dest_node_index

    def _canonize_suffix(self, suffix):
        if not suffix.explicit():
            e = self.edges[suffix.source_node_index, self.string[suffix.f_char]]
            if e.length <= suffix.length:
                suffix.f_char += e.length + 1
                suffix.source_node_index = e.dest_node_index
                self._canonize_suffix(suffix)
                

 

    def DFS_descendent(self, node_index):
        for child in self.nodes[node_index].child:
            self.nodes[child].d += self.nodes[node_index].d
            self.DFS_descendent(child)
            self.nodes[node_index].descendant += self.nodes[child].descendant

    def fix_suffix_index(self):
        for key in self.edges:
            e = self.edges[key]
            if len(self.nodes[e.dest_node_index].child) == 0:
                self.nodes[e.dest_node_index].suffix_index = self.N - self.nodes[e.dest_node_index].d + 1


    def repair(self):
        self.edges_2 = {}
        ed = {}
        
        for key in self.edges:
            e = self.edges[key]            
            ed[(e.source_node_index, self.string[e.f_char])] = e
            self.nodes[e.dest_node_index].d = e.length + 1
            
            self.edges_2[(e.source_node_index, e.dest_node_index)] = e
            self.nodes[e.source_node_index].child.append(e.dest_node_index)
            self.nodes[e.dest_node_index].parent = e.source_node_index
        
            
        self.edges = ed
        for node in self.nodes:
            if node.child == []:
                node.descendant = 1
        
        self.DFS_descendent(0)
        
        ed1 = {}
        self.fix_suffix_index()
        for key in self.edges:
            e = self.edges[key]
            if ">" in self.string[e.f_char : e.l_char]:
                index = self.string[e.f_char : e.l_char].index('>')
                e.l_char = index + e.f_char
            if self.string[e.f_char - 1] != '>':
                ed1[(e.source_node_index, self.string[e.f_char])] = e
        self.edges = ed1
        

    def find_substring(self, substring):
        if not substring:
            return 0, -1
        if self.case_insensitive:
            substring = substring.lower()
        curr_node = 0
        i = 0
        while True:
            edge = self.edges.get((curr_node, substring[i]))
            if not edge:
                return curr_node, -1
            ln = min(edge.length + 1, len(substring) - i)
            if substring[i:i + ln] != self.string[edge.f_char:edge.f_char + ln]:
                return curr_node, -1
            i += edge.length + 1
            if i >= len(substring):
                break
            curr_node = edge.dest_node_index

        return edge.dest_node_index, edge.f_char - len(substring) + ln
        
    def has_substring(self, substring):
        return self.find_substring(substring) != -1
    
    def DFS_position(self, node_index):
        if self.nodes[node_index].child == []:
            return [self.nodes[node_index].suffix_index]
        position = []
        for child in self.nodes[node_index].child:
            position += self.DFS_position(child)
        return position
        
    def find_all_sub(self, substring):
        a = self.find_substring(substring)
        if a[1] > -1:
            positions = self.DFS_position(a[0])
            self.strings_pos.append(self.N + 1)
            
            if self.strings_num > 1:
                final = ""
                for pos in positions:
                    string_num = list(map(lambda i: i> pos, self.strings_pos)).index(True)
                    final += "In String %d at position %d.\n"%(string_num, pos - self.strings_pos[string_num - 1])
                return final
            final = "Happend at positions: "
            for pos in positions:
                final += str(pos) + " "
            return final
        return "Couldn't find!"
    
    def find_k_sub(self, k):
        c_nodes = self.nodes[:]
        c_nodes.sort(key=lambda x: x.d, reverse = True)
        flag = False
        for node in c_nodes:
            if node.descendant >= k:
                f_node = node
                flag = True
                index = self.nodes.index(f_node)
                break
        if flag:
            s = ""
            while f_node.parent != None:
                e = self.edges_2[(f_node.parent, index)]
                s = self.string[e.f_char : e.l_char] + self.string[e.l_char] + s
                index = f_node.parent
                f_node = self.nodes[index]
            final = self.find_all_sub(s)
            return s + "\n" + final
        return "Couldn't find!"
    
    def sub_k_strings(self, k):
        c_nodes = self.nodes[:]
        c_nodes.sort(key=lambda x: x.d, reverse = True)
        flag = False
        for node in c_nodes:
            if len(node.child) >= k:
                f_node = node
                flag = True
                index = self.nodes.index(f_node)
                break
        if flag:
            s = ""
            while f_node.parent != None:
                e = self.edges_2[(f_node.parent, index)]
                s = self.string[e.f_char : e.l_char] + self.string[e.l_char] + s
                index = f_node.parent
                f_node = self.nodes[index]
            final = self.find_all_sub(s)
            return s + "\n" + final
        return "Couldn't find!"        

    def longest_commen_sub(self):
        c_nodes = self.nodes[:]
        c_nodes.sort(key=lambda x: x.d, reverse = True)
        flag = False
        for node in c_nodes:
            if len(node.child) == 2:
                index = self.nodes.index(node)
                last1 = self.edges_2[(index, node.child[0])].l_char
                last2 = self.edges_2[(index, node.child[1])].l_char
                s = self.string[last1] + self.string[last2]
                if s == ">$" or s =="$>":
                    f_node = node
                    flag = True
                break
        if flag:
            s = ""
            while f_node.parent != None:
                e = self.edges_2[(f_node.parent, index)]
                s = self.string[e.f_char : e.l_char] + self.string[e.l_char] + s
                index = f_node.parent
                f_node = self.nodes[index]
            if len(s) > 2:
                final = self.find_all_sub(s)
                return s + "\n" + final
        return "Couldn't find!"