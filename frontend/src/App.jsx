import React, { useState, useEffect, useRef } from 'react';
import {
  ChakraProvider, Box, Flex, Text, VStack, HStack, IconButton, Button,
  Input, Textarea, Badge, Spinner, useToast, Divider, Avatar,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton,
  useDisclosure, Tooltip, Collapse, extendTheme, Progress, SimpleGrid, Stat, StatLabel, StatNumber, StatHelpText
} from '@chakra-ui/react';
import { 
  Inbox, Send, Star, Trash2, RefreshCw, Zap, Settings, 
  MessageSquare, X, AlertCircle, Bot, Search, FileEdit, RotateCcw, PenSquare
} from 'lucide-react';
import axios from 'axios';
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from 'react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// --- API CONFIGURATION ---
const API_URL = "http://localhost:8000";
const api = axios.create({ baseURL: API_URL });

// --- THEME ---
const theme = extendTheme({
  config: { initialColorMode: "dark", useSystemColorMode: false },
  styles: {
    global: {
      body: { bg: "gray.900", color: "white" },
      "::-webkit-scrollbar": { width: "6px" },
      "::-webkit-scrollbar-track": { bg: "transparent" },
      "::-webkit-scrollbar-thumb": { bg: "gray.700", borderRadius: "24px" },
    }
  },
  components: {
    Button: { baseStyle: { _focus: { boxShadow: "none" } } },
    Text: { baseStyle: { color: "gray.100" } }
  }
});

const queryClient = new QueryClient();

// --- COMPONENTS ---

// 1. SIDEBAR
const Sidebar = ({ currentView, setView, onOpenBrain }) => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  // Processing State
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressValue, setProgressValue] = useState(0);

  // Stats Data
  const { data: emails } = useQuery('emails', () => api.get("/emails").then(res => res.data));
  const taskCount = emails?.filter(e => e.category === 'Task').length || 0;
  const meetingCount = emails?.filter(e => e.category === 'Meeting').length || 0;

  const loadInboxMutation = useMutation(() => api.post("/ingest/load"), {
    onSuccess: (data) => {
      queryClient.invalidateQueries('emails');
      toast({ title: "Inbox Loaded", description: data.data.message, status: "success", duration: 2000 });
    }
  });

  const resetMutation = useMutation(() => api.post("/system/reset"), {
    onSuccess: () => {
      queryClient.invalidateQueries('emails');
      toast({ title: "System Reset", status: "warning", duration: 2000 });
    }
  });

  const processAI = async () => {
    setIsProcessing(true);
    setProgressValue(10); // Start
    
    // Simulate progress while waiting for backend (Optimistic UI)
    const interval = setInterval(() => {
        setProgressValue(old => {
            if (old >= 90) return 90;
            return old + Math.random() * 10;
        });
    }, 500);

    try {
        await api.post("/ingest/process");
        clearInterval(interval);
        setProgressValue(100);
        queryClient.invalidateQueries('emails');
        toast({ title: "AI Analysis Complete", status: "success", duration: 2000 });
        setTimeout(() => {
            setIsProcessing(false);
            setProgressValue(0);
        }, 500);
    } catch (e) {
        clearInterval(interval);
        setIsProcessing(false);
        toast({ title: "Error Processing", status: "error" });
    }
  };

  return (
    <Box w="260px" h="100vh" bg="gray.900" borderRight="1px solid" borderColor="gray.800" py={4} display="flex" flexDirection="column">
      
      {/* Progress Modal Overlay */}
      <Modal isOpen={isProcessing} isCentered closeOnOverlayClick={false}>
        <ModalOverlay backdropFilter="blur(4px)" />
        <ModalContent bg="gray.800" borderColor="gray.600" p={6} textAlign="center">
            <Text fontSize="lg" fontWeight="bold" mb={4} color="white">AI Agent Working...</Text>
            <Progress hasStripe isAnimated value={progressValue} colorScheme="blue" borderRadius="md" h="12px" />
            <Text fontSize="sm" color="gray.400" mt={3}>Categorizing & Extracting Tasks</Text>
        </ModalContent>
      </Modal>

      <HStack px={6} mb={6} spacing={3}>
        <Box p={1.5} bg="blue.500" borderRadius="md"><Bot color="white" size={20} /></Box>
        <Text fontSize="lg" fontWeight="bold" letterSpacing="tight" color="white">AgentMail</Text>
      </HStack>

      <Box px={4} mb={6}>
        <Button 
          leftIcon={<PenSquare size={18}/>} 
          bg="white" color="gray.900" 
          _hover={{ bg: "gray.200" }}
          size="lg" width="100%" borderRadius="xl" shadow="md" fontWeight="bold"
        >
          Compose
        </Button>
      </Box>

      {/* AI Controls */}
      <VStack px={4} align="stretch" spacing={2} mb={4}>
        <Text fontSize="xs" fontWeight="bold" color="gray.500" px={3}>AI CONTROLS</Text>
        <Button 
          leftIcon={<RefreshCw size={16}/>} 
          justifyContent="flex-start" variant="ghost" size="sm" color="gray.300"
          _hover={{ bg: "gray.800", color: "white" }}
          isLoading={loadInboxMutation.isLoading}
          onClick={() => loadInboxMutation.mutate()}
        >
          Load Inbox
        </Button>
        <Button 
          leftIcon={<Zap size={16}/>} 
          justifyContent="flex-start" variant="ghost" size="sm" color="yellow.300"
          _hover={{ bg: "gray.800", color: "yellow.200" }}
          onClick={processAI}
        >
          Process AI
        </Button>
      </VStack>

      {/* Stats Panel */}
      <Box px={4} mb={4}>
          <SimpleGrid columns={2} spacing={2}>
              <Box bg="gray.800" p={2} borderRadius="md" border="1px solid" borderColor="gray.700">
                  <Stat size="sm">
                      <StatLabel color="gray.400">Tasks</StatLabel>
                      <StatNumber color="red.300">{taskCount}</StatNumber>
                  </Stat>
              </Box>
              <Box bg="gray.800" p={2} borderRadius="md" border="1px solid" borderColor="gray.700">
                  <Stat size="sm">
                      <StatLabel color="gray.400">Meetings</StatLabel>
                      <StatNumber color="blue.300">{meetingCount}</StatNumber>
                  </Stat>
              </Box>
          </SimpleGrid>
      </Box>

      {/* Navigation */}
      <VStack align="stretch" spacing={0} flex={1}>
        <NavButton icon={Inbox} label="Inbox" isActive={currentView === 'inbox'} onClick={() => setView('inbox')} />
        <NavButton icon={Star} label="Starred" isActive={currentView === 'starred'} onClick={() => setView('starred')} />
        <NavButton icon={FileEdit} label="Drafts" isActive={currentView === 'drafts'} onClick={() => setView('drafts')} />
        <NavButton icon={Trash2} label="Trash" isActive={currentView === 'trash'} onClick={() => setView('trash')} />
      </VStack>

      <Divider my={4} borderColor="gray.800" />
      
      <VStack px={4} align="stretch" spacing={1}>
        <Button 
          leftIcon={<Settings size={18}/>} w="full" variant="ghost" 
          justifyContent="flex-start" onClick={onOpenBrain} color="gray.400"
          _hover={{ bg: "gray.800", color: "white" }}
        >
          Agent Brain
        </Button>
        
        <Button 
          leftIcon={<RotateCcw size={18}/>} w="full" 
          justifyContent="flex-start" colorScheme="red" variant="outline" size="sm"
          onClick={() => resetMutation.mutate()}
          mt={2}
        >
          Reset System
        </Button>
      </VStack>
    </Box>
  );
};

const NavButton = ({ icon: Icon, label, isActive, onClick }) => (
  <Flex 
    as="button"
    align="center" 
    px={6} py={2}
    bg={isActive ? "blue.900" : "transparent"}
    color={isActive ? "blue.100" : "gray.400"}
    borderRight={isActive ? "3px solid" : "3px solid transparent"}
    borderColor={isActive ? "blue.400" : "transparent"}
    _hover={{ bg: "gray.800", color: "gray.200" }}
    onClick={onClick}
    cursor="pointer"
    transition="all 0.2s"
  >
    <Icon size={18} />
    <Text ml={4} fontSize="sm" fontWeight={isActive ? "bold" : "medium"} flex={1} textAlign="left">{label}</Text>
  </Flex>
);

// 2. EMAIL LIST
const EmailList = ({ currentView, selectedEmailId, setSelectedEmailId }) => {
  const { data: emails, isLoading, refetch } = useQuery('emails', () => api.get("/emails").then(res => res.data));
  const [filter, setFilter] = useState("All");
  
  const toggleStarMutation = useMutation(
    ({ id, isStarred }) => api.post(`/emails/${id}/star`, { email_id: id, is_starred: isStarred }),
    { onSuccess: () => refetch() }
  );

  if (isLoading) return <Flex justify="center" align="center" h="full" w="full"><Spinner color="blue.500" /></Flex>;

  // View Logic
  let displayEmails = emails || [];
  
  if (currentView === 'starred') {
      displayEmails = displayEmails.filter(e => e.is_starred);
  } else if (currentView === 'drafts') {
      displayEmails = displayEmails.filter(e => e.is_drafted);
  } else if (currentView === 'trash') {
      displayEmails = []; // Empty for demo
  }

  // Category Filter Logic
  const filteredEmails = displayEmails.filter(e => {
    const cat = e.category || "Uncategorized";
    return filter === "All" ? true : cat === filter;
  });

  return (
    <Flex direction="column" h="100vh" bg="gray.900" flex={1}>
      {/* Toolbar */}
      <Flex p={3} borderBottom="1px solid" borderColor="gray.800" align="center" justify="space-between">
        <HStack spacing={4}>
          <Text fontSize="xl" fontWeight="bold" ml={2} color="white" textTransform="capitalize">{currentView}</Text>
          <Box h="20px" w="1px" bg="gray.700" />
          <HStack spacing={2}>
            {["All", "Task", "Meeting", "Project Update", "Spam"].map(cat => (
               <Button 
                 key={cat} size="xs" borderRadius="full" px={4}
                 variant={filter === cat ? "solid" : "outline"}
                 colorScheme={filter === cat ? "blue" : "gray"}
                 color={filter === cat ? "white" : "gray.400"}
                 _hover={{ bg: filter === cat ? "blue.600" : "gray.700" }}
                 onClick={() => setFilter(cat)}
               >
                 {cat}
               </Button>
            ))}
          </HStack>
        </HStack>
        <IconButton icon={<Search size={18} />} variant="ghost" aria-label="Search" color="gray.400" _hover={{ bg: "gray.800", color: "white" }}/>
      </Flex>

      {/* Email List */}
      <Box flex={1} overflowY="auto">
        {filteredEmails.length === 0 ? (
            <Flex h="full" justify="center" align="center" color="gray.500">No emails found</Flex>
        ) : (
            filteredEmails.map(email => (
            <Flex 
                key={email.id} 
                px={4} py={3} 
                borderBottom="1px solid" borderColor="gray.800" 
                cursor="pointer"
                bg={selectedEmailId === email.id ? "rgba(59, 130, 246, 0.15)" : "transparent"}
                _hover={{ bg: "gray.800", boxShadow: "inset 2px 0 0 #3b82f6" }}
                align="center"
                onClick={() => setSelectedEmailId(email.id)}
                transition="background 0.1s"
            >
                {/* Star */}
                <IconButton 
                    icon={<Star size={16} fill={email.is_starred ? "#ECC94B" : "none"} color={email.is_starred ? "#ECC94B" : "gray"} />}
                    variant="ghost" size="xs" mr={2}
                    onClick={(e) => { e.stopPropagation(); toggleStarMutation.mutate({ id: email.id, isStarred: !email.is_starred }); }}
                />

                {/* Sender */}
                <Text w="180px" fontWeight={selectedEmailId === email.id ? "bold" : "medium"} color="gray.200" noOfLines={1} fontSize="sm">
                {email.sender}
                </Text>
                
                {/* Content */}
                <HStack flex={1} spacing={3} overflow="hidden">
                <CategoryBadge category={email.category} />
                <Text color="gray.300" fontSize="sm" fontWeight="medium" noOfLines={1}>
                    {email.subject}
                </Text>
                <Text color="gray.500" fontSize="sm" noOfLines={1}>
                    - {email.body}
                </Text>
                </HStack>

                {/* Date */}
                <Text fontSize="xs" color="gray.500" w="80px" textAlign="right" fontWeight="bold">
                {new Date(email.received_date).toLocaleDateString([], {month: 'short', day: 'numeric'})}
                </Text>
            </Flex>
            ))
        )}
      </Box>
    </Flex>
  );
};

const CategoryBadge = ({ category }) => {
  const colorMap = {
    Task: "red",
    Meeting: "blue",
    Newsletter: "green",
    "Project Update": "orange",
    Spam: "gray",
    Uncategorized: "gray"
  };
  const cat = category || "Uncategorized";
  return (
    <Badge colorScheme={colorMap[cat]} variant="subtle" borderRadius="md" px={1.5} fontSize="10px" textTransform="uppercase" letterSpacing="wider">
      {cat}
    </Badge>
  );
};

// 3. READING PANE
const ReadingPane = ({ emailId, onClose }) => {
  const queryClient = useQueryClient();
  const toast = useToast();
  
  const { data: emails } = useQuery('emails');
  const email = emails?.find(e => e.id === emailId);
  const [draftText, setDraftText] = useState("");

  useEffect(() => {
    if (email?.reply_draft) setDraftText(email.reply_draft);
    else setDraftText("");
  }, [email]);

  const generateDraftMutation = useMutation(() => api.post(`/emails/${emailId}/draft`), {
    onSuccess: (res) => {
      setDraftText(res.data.draft);
      queryClient.invalidateQueries('emails');
      toast({ title: "Draft Generated", status: "success" });
    }
  });

  const saveDraftMutation = useMutation(() => api.post(`/emails/save-draft`, { email_id: emailId, draft_text: draftText }), {
    onSuccess: () => {
      queryClient.invalidateQueries('emails');
      toast({ title: "Draft Saved", status: "success" });
    }
  });

  const toggleStarMutation = useMutation(
    () => api.post(`/emails/${emailId}/star`, { email_id: emailId, is_starred: !email.is_starred }),
    { onSuccess: () => queryClient.invalidateQueries('emails') }
  );

  if (!email) return <Flex flex={1} bg="gray.900" justify="center" align="center" borderLeft="1px solid" borderColor="gray.800"><Text color="gray.500">Select an email to view details</Text></Flex>;

  const actionItems = email.action_items ? JSON.parse(email.action_items).tasks : [];

  return (
    <Flex w="600px" h="100vh" bg="gray.900" borderLeft="1px solid" borderColor="gray.800" direction="column">
      <Flex p={5} borderBottom="1px solid" borderColor="gray.800" justify="space-between" align="start">
        <Box flex={1}>
          <Text fontSize="xl" fontWeight="bold" mb={2} color="white">{email.subject}</Text>
          <HStack spacing={3} mb={1}>
             <Avatar size="xs" name={email.sender} />
             <Text fontWeight="bold" fontSize="sm" color="gray.300">{email.sender}</Text>
             <CategoryBadge category={email.category} />
          </HStack>
          <Text fontSize="xs" color="gray.500">{email.received_date}</Text>
        </Box>
        <HStack>
            <IconButton 
                icon={<Star size={18} fill={email.is_starred ? "#ECC94B" : "none"} />} 
                variant="ghost" aria-label="Star" 
                color={email.is_starred ? "yellow.400" : "gray.400"} 
                onClick={() => toggleStarMutation.mutate()}
            />
            <IconButton icon={<X size={18}/>} variant="ghost" onClick={onClose} aria-label="Close" color="gray.400" _hover={{color: "white"}} />
        </HStack>
      </Flex>

      <Box p={6} flex={1} overflowY="auto">
        {actionItems && actionItems.length > 0 && (
          <Box mb={6} bg="rgba(236, 201, 75, 0.1)" borderLeft="4px solid" borderColor="yellow.500" borderRadius="sm" p={4}>
             <HStack mb={2} color="yellow.300"><AlertCircle size={16} /><Text fontWeight="bold" fontSize="sm">Suggested Actions</Text></HStack>
             <VStack align="start" pl={6} spacing={1}>
               {actionItems.map((item, i) => (
                 <Text key={i} fontSize="sm" color="yellow.100">• {item.description} <Text as="span" color="yellow.500" fontSize="xs">({item.deadline})</Text></Text>
               ))}
             </VStack>
          </Box>
        )}

        <Text whiteSpace="pre-wrap" fontSize="sm" lineHeight="tall" color="gray.200">{email.body}</Text>
      </Box>

      <Box p={4} borderTop="1px solid" borderColor="gray.800" bg="gray.800">
        <Flex justify="space-between" align="center" mb={3}>
            <HStack><Bot size={16} color="#60A5FA"/><Text fontWeight="bold" fontSize="sm" color="blue.300">AI Reply Draft</Text></HStack>
            <Button 
              size="xs" leftIcon={<Zap size={14}/>} 
              colorScheme="blue" variant="outline"
              isLoading={generateDraftMutation.isLoading}
              onClick={() => generateDraftMutation.mutate()}
            >
              Regenerate
            </Button>
        </Flex>

        <Box position="relative">
            {!draftText && !generateDraftMutation.isLoading && (
                 <Flex justify="center" align="center" h="100px" border="1px dashed" borderColor="gray.600" borderRadius="md" _hover={{borderColor: "gray.400", cursor: "pointer"}} onClick={() => generateDraftMutation.mutate()}>
                    <Text fontSize="sm" color="gray.400">Click to Generate Draft with AI</Text>
                 </Flex>
            )}
            
            {(draftText || generateDraftMutation.isLoading) && (
                <>
                <Textarea 
                    value={draftText} 
                    onChange={(e) => setDraftText(e.target.value)}
                    h="150px" bg="gray.900" border="1px solid" borderColor="gray.600"
                    color="white"
                    placeholder="Generating..."
                    fontSize="sm" p={3}
                    _focus={{ borderColor: "blue.500" }}
                />
                <Flex justify="flex-end" mt={2}>
                    <Button 
                        size="sm" colorScheme="blue" 
                        onClick={() => saveDraftMutation.mutate()}
                        isLoading={saveDraftMutation.isLoading}
                    >
                        Save Draft
                    </Button>
                </Flex>
                </>
            )}
        </Box>
      </Box>
    </Flex>
  );
};

// 4. CHAT WIDGET
const ChatWidget = () => {
  const { isOpen, onToggle } = useDisclosure();
  const [msg, setMsg] = useState("");
  const [history, setHistory] = useState([{ role: 'assistant', content: 'How can I help with your emails today?' }]);
  const scrollRef = useRef(null);

  const chatMutation = useMutation((message) => api.post("/chat", { message }), {
    onSuccess: (res) => {
      setHistory(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    }
  });

  const send = () => {
    if(!msg.trim()) return;
    const userMsg = msg;
    setHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setMsg("");
    chatMutation.mutate(userMsg);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history, isOpen]);

  return (
    <Box position="fixed" bottom={6} right={6} zIndex={100}>
      <Collapse in={isOpen} animateOpacity>
        <Box w="380px" h="500px" bg="gray.800" borderRadius="lg" shadow="2xl" border="1px solid" borderColor="gray.600" mb={3} display="flex" flexDirection="column">
          <Flex p={3} bg="blue.600" borderTopRadius="lg" align="center" justify="space-between">
            <HStack><Bot color="white" size={18}/><Text fontWeight="bold" fontSize="sm" color="white">Agent Chat</Text></HStack>
          </Flex>
          <Box ref={scrollRef} flex={1} p={4} overflowY="auto" css={{"&::-webkit-scrollbar": {display: "none"}}}>
            {history.map((h, i) => (
              <Flex key={i} justify={h.role === 'user' ? 'flex-end' : 'flex-start'} mb={3}>
                <Box maxW="90%" p={3} borderRadius="md" fontSize="sm" bg={h.role === 'user' ? 'blue.600' : 'gray.700'} color="white" boxShadow="sm">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                        ul: ({node, ...props}) => <ul style={{paddingLeft: '20px', marginBottom: '8px'}} {...props} />,
                        li: ({node, ...props}) => <li style={{marginBottom: '4px'}} {...props} />,
                        p: ({node, ...props}) => <p style={{marginBottom: '8px'}} {...props} />,
                        strong: ({node, ...props}) => <span style={{fontWeight: 'bold', color: '#90CDF4'}} {...props} />
                    }}
                  >
                    {h.content}
                  </ReactMarkdown>
                </Box>
              </Flex>
            ))}
            {chatMutation.isLoading && <Text fontSize="xs" color="gray.400" ml={2} fontStyle="italic">Thinking...</Text>}
          </Box>
          <HStack p={3} borderTop="1px solid" borderColor="gray.700" bg="gray.800" borderBottomRadius="lg">
            <Input placeholder="Ask a question..." value={msg} onChange={e => setMsg(e.target.value)} size="sm" borderRadius="full" onKeyPress={e => e.key === 'Enter' && send()} bg="gray.700" border="none" color="white" _placeholder={{ color: "gray.400" }} _focus={{ ring: 2, ringColor: "blue.500" }}/>
            <IconButton icon={<Send size={16}/>} onClick={send} size="sm" isRound colorScheme="blue" aria-label="Send" />
          </HStack>
        </Box>
      </Collapse>
      <Tooltip label="Chat with Agent" placement="left">
        <IconButton icon={isOpen ? <X /> : <MessageSquare />} onClick={onToggle} colorScheme="blue" size="lg" isRound shadow="lg" aria-label="Chat Toggle" />
      </Tooltip>
    </Box>
  );
};

// 5. AGENT BRAIN MODAL
const AgentBrain = ({ isOpen, onClose }) => {
  const { data: prompts } = useQuery('prompts', () => api.get("/prompts").then(res => res.data));
  const queryClient = useQueryClient();
  const toast = useToast();
  const [localPrompts, setLocalPrompts] = useState({});

  useEffect(() => { if (prompts) setLocalPrompts(prompts); }, [prompts]);

  const updateMutation = useMutation((key) => api.post("/prompts", { key, text: localPrompts[key] }), {
    onSuccess: (res) => {
      queryClient.invalidateQueries('prompts');
      toast({ title: "Updated", description: res.data.message, status: "success" });
    }
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay backdropFilter="blur(2px)"/>
      <ModalContent bg="gray.800" borderColor="gray.700">
        <ModalHeader color="white">🧠 Agent Configuration</ModalHeader>
        <ModalCloseButton color="white" />
        <ModalBody pb={6}>
          <VStack spacing={6} align="stretch">
            {["categorization", "action_items", "auto_reply"].map(key => (
              <Box key={key}>
                <Flex justify="space-between" mb={2} align="center">
                  <Text fontWeight="bold" fontSize="sm" textTransform="uppercase" color="gray.400">{key.replace("_", " ")}</Text>
                  <Button size="xs" colorScheme="green" onClick={() => updateMutation.mutate(key)}>Save</Button>
                </Flex>
                <Textarea value={localPrompts[key] || ""} onChange={(e) => setLocalPrompts({...localPrompts, [key]: e.target.value})} h="120px" fontSize="sm" bg="gray.900" color="white" fontFamily="monospace" border="1px solid" borderColor="gray.600"/>
              </Box>
            ))}
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

function App() {
  const [selectedEmailId, setSelectedEmailId] = useState(null);
  const [currentView, setView] = useState('inbox'); // 'inbox', 'starred', 'drafts', 'trash'
  const { isOpen: isBrainOpen, onOpen: onOpenBrain, onClose: onCloseBrain } = useDisclosure();

  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        <Flex h="100vh" overflow="hidden">
          <Sidebar currentView={currentView} setView={setView} onOpenBrain={onOpenBrain} />
          <EmailList currentView={currentView} selectedEmailId={selectedEmailId} setSelectedEmailId={setSelectedEmailId} />
          {selectedEmailId && <ReadingPane emailId={selectedEmailId} onClose={() => setSelectedEmailId(null)} />}
          <ChatWidget />
          <AgentBrain isOpen={isBrainOpen} onClose={onCloseBrain} />
        </Flex>
      </ChakraProvider>
    </QueryClientProvider>
  );
}

export default App;