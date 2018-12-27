#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <fcntl.h> // for open
#include <unistd.h> // for close
#include <errno.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>

int cCount;
int clientCount;

struct mylist {
	char pName[50];
	char active[10];
	int pID;
	time_t tStart;
	time_t tEnd;
	char start[100];
	char end[100];
	double elapsed;
	
	
  
} mylist[1000];

struct clientList{
	int id;
	//int sfd;
	int pid;
	int pd[2];
	int pd2[2];
	char active[10];
	char ip[100];
	int port;
	

}clientList[1000];


int findIndex(int pid){
	for(int i=0;i<cCount;i++){

		if(strcmp(mylist[i].active,"True")==0){
			if(mylist[i].pID==pid){

				return i;
			}
		}

	}
	return -1;

}

int findName(char *token){
	for(int i=0;i<cCount;i++){

		if(strcmp(mylist[i].active,"True")==0){
			if(strcmp(mylist[i].pName,token)==0){

				return mylist[i].pID;
			}
		}

	}
	return -1;

}



void addM(char buff2[], char *token){


	int sum=0;
	int n=0;
	token = strtok(NULL," ");
	while( token!=NULL){
		n=atoi(token);
		sum+=n;
		token = strtok(NULL," ");



	}

	int pCount = sprintf(buff2,"Addition Answer: %d\n",sum);

}

void subM(char buff2[], char *token){
	int sum=0;
	int n=0;
	token = strtok(NULL," ");
	while( token!=NULL){
		n=atoi(token);
		sum-=n;
		token = strtok(NULL," ");



	}

	int pCount = sprintf(buff2,"Subtraction Answer: %d\n",sum);



}
void multM(char buff2[], char *token){

	
	int sum=1;
	int n=0;
	token = strtok(NULL," ");

	if(token == NULL|| strcmp("\n",token)==0){ sum=0;}

	bool sumset=false;
	while( token!=NULL){
		n=atoi(token);

		if(n==0){ 
			if(strcmp("0",token) == 0 || strcmp("0\n",token) == 0 || strcmp(" ",token) == 0 || strcmp(" \n",token) == 0 ){
    				n=0;}
			else{
				strcpy(buff2,"Invalid Data\n");
				return;}				
		}
		else if(!sumset){
				sumset=true;
				sum=n;
				token = strtok(NULL," ");
				continue;
			}
		
		sum*=n;
		token = strtok(NULL," \n");
		}

	int pCount = sprintf(buff2,"Multiplication Answer: %d\n",sum);





}
void divM(char buff2[], char *token){


	int sum=1;
	int n=0;
	token = strtok(NULL," ");

	if(token == NULL|| strcmp("\n",token)==0){ sum=0;}

	bool sumset=false;
	bool divZero=false;
	while( token!=NULL){
		n=atoi(token);

		if(n==0){ 
			if(strcmp("0",token) == 0 || strcmp("0\n",token) == 0 || strcmp(" ",token) == 0 || strcmp(" \n",token) == 0 ){
    				n=0;
				divZero=true; break;}
			else{
				strcpy(buff2,"Invalid Data\n");
				return;}				
		}
		else if(!sumset){
				sumset=true;
				sum=n;
				token = strtok(NULL," ");
				continue;
			}
		
		sum/=n;
		token = strtok(NULL," \n");
		}
	if(divZero){
		strcpy(buff2,"Error: Dividing by Zero\n");}
	else{
		int pCount = sprintf(buff2,"Division Answer: %d\n",sum);}


}






void listM(char buff2[], char *token){

	bool total=true;

	token = strtok(NULL," \n");
	if(token != NULL){
		if(strcmp(token,"active") ==0 || strcmp(token,"active\n")==0){
			total=false;
		}
	}						
	
	
	
		buff2[0]='\0';
		strcpy(buff2,"\nS.NO\tNAME\t\t\tID\tACTIVE\tST\t\tET\t\tTT\n");
		int processCount=1;
		for(int i=0 ; i<cCount ; i++){

			//DOUBLE TIME CALCULATION
			double totalTime = difftime(mylist[i].tEnd,mylist[i].tStart);
			if( strcmp(mylist[i].end,"--    ")==0){
				totalTime = difftime(time(NULL),mylist[i].tStart);
	
			}

			//ADDING SPACES FOR LIST
			char nameBuff[100];
			bzero(nameBuff,100);
			strcpy(nameBuff,mylist[i].pName);
			while(strlen(nameBuff)<16){
				nameBuff[strlen(nameBuff)]=' ';
				nameBuff[strlen(nameBuff)+1]='\0';
			}

			

			if(total){
								
				

				int pCount = sprintf(&buff2[strlen(buff2)],"%d\t%s\t%d\t%s\t%s  \t%s      \t%d\n",processCount,nameBuff,mylist[i].pID,mylist[i].active,mylist[i].start,mylist[i].end,(int)totalTime);
				processCount++;							
			}
			else if(strcmp(mylist[i].active,"True")==0){
				int pCount = sprintf(&buff2[strlen(buff2)],"%d\t%s\t%d\t%s\t%s  \t--          \t%d\n",processCount,nameBuff,mylist[i].pID,mylist[i].active,mylist[i].start,(int)totalTime);
				processCount++;							
			}
		}

		if(cCount == 0 || processCount ==1){
			strcpy(buff2,"Empty List\n");

		}


}
void runM(char buff2[], char *token){

	token=strtok(NULL," \n");
	if(token==NULL){	strcpy(buff2,"Not Enough Arguments\n");	}
	else{

		int rpd[2]; pipe(rpd);
		fcntl(rpd[1],F_SETFD,FD_CLOEXEC);


		int pid = fork();

		if(pid == 0){

			close(rpd[0]);

			int execCount = execlp(token,token,NULL);

			if(execCount == -1){
				write(rpd[1],"F",1);
				//strcpy(buff2,"No such process exists.\n");

				exit(99);
			}

		}
		else if(pid>0){

			close(rpd[1]);
			char mybuff[1];
			int n = read(rpd[0],mybuff,1);

			if(n==0){

				strcpy(buff2,"Exec Success\n");
				strcpy(mylist[cCount].pName,token);
				
				

				
				mylist[cCount].pID=pid;
				strcpy(mylist[cCount].active,"True");
				


				mylist[cCount].tStart=time(NULL);
				mylist[cCount].tEnd=time(NULL);
				strcpy(mylist[cCount].end,"--    ");
				struct tm *tstart = localtime(&mylist[cCount].tStart);
				sprintf(mylist[cCount].start,"%d:%d:%d",tstart->tm_hour,tstart->tm_min,tstart->tm_sec);
				

				cCount++;
			}
			else{

				strcpy(buff2,"Exec Failed\n");
			}
			close(rpd[0]);


		}

	}


}


void killAllM(){

	for(int i=0;i<cCount;i++){

			if(strcmp(mylist[i].active,"True")==0){
				kill(mylist[i].pID,SIGKILL);
			}

		}




}

void killM(char buff2[], char *token){
	
	token = strtok(NULL," \n");
	if(token==NULL){	strcpy(buff2,"Not Enough Arguments\n");	return;}
	else if(strcmp(token,"pid") ==0){
		
		token = strtok(NULL," \n");
		if(token==NULL){	strcpy(buff2,"Enter a valid Process ID\n");	return;}
		int kpid;
		int scanCount = sscanf(token,"%d",&kpid);
		if(scanCount<0){ strcpy(buff2,"Enter a valid number"); return; }

		if(findIndex(kpid)>=0){
			kill(kpid,SIGKILL);
			strcpy(buff2,"Process Terminated\n");

		}
		else{

		strcpy(buff2,"Process ID doesn't exist in your active table\n");
		}
			
	}
	else if(strcmp(token,"name") ==0){
		
		token = strtok(NULL," \n");
		if(token==NULL){	strcpy(buff2,"Enter a Valid Name\n");	return;}
		int kpid = findName(token);
		

		if(kpid>=0){
			kill(kpid,SIGKILL);
			strcpy(buff2,"Process Terminated\n");

		}
		else{

		strcpy(buff2,"Process name doesn't exist in your active table\n");
		}
	}
	else if(strcmp(token,"all") ==0){
		
		killAllM();
		strcpy(buff2,"All Processes Killed\n");
	}
	else{
		strcpy(buff2,"Not Enough Arguments\n");
		
	}
			



}


void helpM(char buff2[], char *token){

	strcpy(buff2,"Addition \t\t-> e.g. \"add 2 2\"\nSubtraction \t\t-> \"sub 2 2\"\nMultiplication \t\t-> \"mul 2 2\"\nDivision \t\t-> \"div 2 2\"\nRun a process \t\t-> \"run gedit\"\nActive Processes\t\t-> \"list active\"\nTotal Processes\t\t-> \"list\"\nKill a Process \t\t-> \"kill name <name>\"\nKill a Process \t\t -> \"kill pid <pid>\"\nExit Program \t\t-> \"exit\"\n");


}



//CLIENT METHODS SIGNALS

void sig_handler(int signo){

	
	int status;

	int pid = 1;
	while(pid > 0){
		 pid = waitpid(-1,&status,WNOHANG);
	
	
		if (WEXITSTATUS(status)==99){
		
		}
		else{
			int index = findIndex(pid);
		
			strcpy(mylist[index].active,"False");

			//end time
			mylist[index].tEnd=time(NULL);
			struct tm *tend = localtime(&mylist[index].tEnd);
			sprintf(mylist[index].end,"%d:%d:%d",tend->tm_hour,tend->tm_min,tend->tm_sec);

		
		
		}
		

	}

}

void sigtermHandler(int signo){
	killAllM();
	exit(1);

}


/*
void sigint_handler(int signo){
	write(1,"\nReceived Signal Interrupt. Are you sure you want to shut server down?\nY/N?\n",sizeof("\nReceived Signal Interrupt. Are you sure you want to shut server down?\nY/N?\n"));
	char buff[100];
	int rCount = read(0,buff,100);
	if(strncmp(buff,"Y",1)==0 || strncmp(buff,"y",1)==0){
		exit(0);
	}
	else{
		write(1,"Server not shut down\n",sizeof("Server not shut down\n"));
	}
}
*/
//


void* clientThread(void *arg){
	int sfd = *((int *) arg);

	char buff[1000];	char buff2[1000];	char messageBuff[1000];
	
	char *token;
			
			
	close(clientList[clientCount].pd[1]);
	close(clientList[clientCount].pd2[0]);

	while(true){
		int pipeRead = read(clientList[clientCount].pd[0],buff,1000);
		
		if(pipeRead == -1){
			perror("Pipe Error");
			exit(1);
		}
		
		if(pipeRead==1){		
			listM(buff2,token);
			int pipeWrite = write(clientList[clientCount].pd2[1],buff2,strlen(buff2));
		}
		else{
			buff[pipeRead] = '\0';
			int pmCount = sprintf(messageBuff,"\nMESSAGE FROM SERVER\n%s",buff);
			write(sfd,messageBuff,pmCount);
			int pipeWriteMessage = write(clientList[clientCount].pd2[1],"Message Sent\n",sizeof("Message Sent\n"));
			
		}
		
		
	}


}


void serverMethods(int sfd, char clientIP[]){
	signal(SIGCHLD,sig_handler);
	signal(SIGTERM,sigtermHandler);
	
	int iCount=0;

	
	char connectBuff[64];
	char endBuff[64];
	int cpCount = sprintf(connectBuff,"Connection Successful with '%s'\n",clientIP);
	int cpCount2 = sprintf(endBuff,"Connection Ended with '%s'\n",clientIP);

	//THREAD CREATION
	pthread_t th2;
	
	int tCount2 = pthread_create(&th2, NULL,clientThread,(void*) &sfd);
	

	write(1,connectBuff,cpCount);
			write(sfd,"Connection Successful\nServer Ready\n",sizeof("Connection Successful\nServer Ready\n"));
			while(true){
				


				char buff[10000]=""; char buff2[10000]="";


				int sRead = read(sfd,buff,sizeof(buff));

				
				
				
				if(sRead < 0){
					perror("Reading from Socket");
					exit(1);
				}
				else if(sRead > 0){
					iCount++;
					
					char *token = strtok(buff," \n");
				
					if(token == NULL){
						strcpy(buff2,"Incorrect Command\n");
					}
					else if(strlen(buff)==1){
						strcpy(buff2,"Incorrect Command\n");
					}
					else if(strcmp(token,"add")==0){

						addM(buff2,token);

					}

					else if(strcmp(token,"sub")==0){

						subM(buff2,token);

					}
					else if(strcmp(token,"mul")==0){

						multM(buff2,token);
		
					}
					else if(strcmp(token,"div")==0){

						divM(buff2,token);

					}
					else if(strcmp(token,"run")==0){

						runM(buff2,token);
			
					}
					else if(strcmp(token,"list")==0){
						
						listM(buff2,token);
					
					}
					else if(strcmp(token,"kill")==0){
						
						killM(buff2,token);
						
			
					}
					else if(strcmp(token,"help")==0){

						helpM(buff2,token);
			
					}
					
					else{
						strcpy(buff2,"Incorrect Command\n");
					}

					char ibuff[sizeof(buff2)+15];
					int ipCount = sprintf(ibuff,"%d| %s",iCount,buff2);
					
					int wCount = write(sfd,ibuff,ipCount);

				}
				else if (sRead == 0){

					write(1,endBuff,cpCount2);
					close(sfd);
					killAllM();
					break;
				}
			}


}







//SERVER METHODS
void listConnM(char buff2[]){

	
	
	
	buff2[0]='\0';
	strcpy(buff2,"S.NO\tIP\t\tPort\tPID\tActive\n");

	for(int i=0;i<clientCount;i++){

		int pCount = sprintf(&buff2[strlen(buff2)],"%d\t%s\t%d\t%d\t%s\n",clientList[i].id,clientList[i].ip,clientList[i].port,clientList[i].pid,clientList[i].active);

	}

	if(clientCount == 0){
		strcpy(buff2,"Empty List\n");

	}

	


}

void listProcessAllM(char buff2[]){
	
	
	for(int i =0;i<clientCount;i++){
		
		
		if(strcmp(clientList[i].active,"True")==0){
			int pipeWrite = write(clientList[i].pd[1],"l",1);
	
			int pipeRead = read(clientList[i].pd2[0],buff2,10000);
			
			int wCount = write(1,buff2,pipeRead);
		}
		

		


	}

	strcpy(buff2,"List Complete\n");



}

void listProcessIpM(char buff2[],char *token){
	int i;
	for(i =0;i<clientCount;i++){
		
		if(strcmp(token,clientList[i].ip)==0){
			if(strcmp(clientList[i].active,"True")==0){
				break;
			}
			

		}


	}
	
	if(i==clientCount){
		strcpy(buff2,"IP doesn't exist in your table or is inactive.\n");
		return;
	}

	
	int pipeWrite = write(clientList[i].pd[1],"l",1);
	
	int pipeRead = read(clientList[i].pd2[0],buff2,10000);
	
	buff2[pipeRead]='\0';

}



void killServerM(char buff2[]){

	for(int i=0;i<clientCount;i++){

		if(strcmp(clientList[i].active,"True")==0){
			
			kill(clientList[i].pid,SIGTERM);
		}
		

	}
		
	if(clientCount == 0){
		strcpy(buff2,"Empty List\n");

	}
	else{
		strcpy(buff2,"Killed Processes\n");
	}

}

void messageServerM(char buff2[], char *token){

	token = strtok(NULL," \n");
	if(token == NULL){
		strcpy(buff2,"Incomplete parameters\n");
		return;
	}

	int i;
	for(i =0;i<clientCount;i++){
		
		if(strcmp(token,clientList[i].ip)==0){
			if(strcmp(clientList[i].active,"True")==0){
				break;
			}
			

		}


	}

	
	if(i==clientCount){
		strcpy(buff2,"IP doesn't exist in your table or is inactive.\n");
		return;
	}

	token = strtok(NULL,"\n");
	
	if(token == NULL){
		strcpy(buff2,"Incomplete parameters\n");
		return;
	}
	char mesgBuff[100];
	int mCount = sprintf(mesgBuff,"\"%s\"\n",token);
	int pipeWrite = write(clientList[i].pd[1],mesgBuff,mCount);
	
	int pipeRead = read(clientList[i].pd2[0],buff2,10000);
	
	buff2[pipeRead]='\0';

	

}

int findIndexServer(int pid){
	for(int i=0;i<clientCount;i++){

		if(strcmp(clientList[i].active,"True")==0){
			if(clientList[i].pid==pid){

				return i;
			}
		}

	}
	return -1;

}

void helpServerM(char buff2[]){

	strcpy(buff2,"list conn \t\t -> List all clients \nlist process \t\t -> List all processes run by clients\nlist process <ip> \t -> list all processes run by the given ip\nkill all \t\t -> kill all clients\n");


}

//SERVER SIGNALS


void sigServer(int signo){
	

	int status;
	int pid = 1;
	while(pid>0){
		pid = waitpid(-1,&status,WNOHANG);
		if(pid != -1){
			int index = findIndexServer(pid);
			if(index == -1){	continue;}
			strcpy(clientList[index].active,"False");
		}
		

	}

	
}


void sigtermHandlerServer(int signo){
	char buff2[100];
	killServerM(buff2);
	exit(1);

}


//SERVER INTERACTIVITY THREAD

void* serverThread(void *arg){
	
	char buff[10000], buff2[10000];
	int rCount = 0;
	int wEndCount =0;
	
	while(true){
		
		bzero(buff,rCount); bzero(buff2,strlen(buff2));

		int wCount = write(1,"--------------------------------\nEnter a command or write 'help'.\n->",68);
		
		rCount = read(1,buff,10000);

		

		char *token = strtok(buff," \n");

		if(token == NULL){
			strcpy(buff2,"Incorrect Instruction\n");
			}
		
		else if(strcmp(token,"list") == 0){

			token = strtok(NULL," \n");
			if(token == NULL){
				strcpy(buff2,"Incorrect Instruction\n");

			}
			else if(strcmp(token,"conn")==0){
				listConnM(buff2);

			}
			else if(strcmp(token,"process")==0){

				token = strtok(NULL," \n");
				if(token == NULL){	
					listProcessAllM(buff2);
				}
				else{
					listProcessIpM(buff2,token);
					

				}
				

				
			}
			else{
			
			strcpy(buff2,"Incorrect Instruction\n");
			}

			

		}
		else if(strcmp(token,"message")==0){

			messageServerM(buff2,token);


		}
		else if(strcmp(token,"kill")==0){
			killServerM(buff2);
			
			

		}
		else if(strcmp(token,"exit")==0){
			
			write(1,"Shutting Down Server\nTerminating all child processes\n",sizeof("Shutting Down Server\nTerminating all child processes\n"));
			killServerM(buff2);
			exit(0);
			
		}
		else if(strcmp(token,"help")==0){

			helpServerM(buff2);

		
		}
		else{
			
			strcpy(buff2,"Incorrect Instruction\n");
		}


		int wEndCount = write(1,buff2,strlen(buff2));
		
		


	}
	
}




//SERVER PARENT STARTING PROCESS
int main(){
	

	

	signal(SIGCHLD,sigServer);
	signal(SIGTERM,sigtermHandlerServer);
	cCount=0;

	//CLIENT INITIALIZE
	clientCount=0;
	struct sockaddr_in client;
	int cSize = sizeof(client);

	//signal(SIGINT,sigint_handler);

	char socketNo[100];
	int sock, length, sockNo;

	struct sockaddr_in server;
	
	server.sin_family = AF_INET;
	server.sin_addr.s_addr = INADDR_ANY;

	
	server.sin_port = htons(0);
	length = sizeof(server);

	//CREATING SOCKET
	sock = socket(AF_INET, SOCK_STREAM, 0);
	if(sock < 0){	perror("Opening socket Stream"); exit(1); }
	
	//BINDING SOCKET
	int bindCount = bind(sock, (struct sockaddr *) &server, length);

	int check = getsockname(sock, (struct sockaddr *) &server, (socklen_t*) &length);
	if (check) {	perror("getting socket name");	exit(1);}

	//PRINT PORT NUMBER
	sockNo = ntohs(server.sin_port);
	

	int socketCount = sprintf(socketNo,"Socket Port Number: %d\n",sockNo);
	write(1,socketNo,socketCount);
	
	//START LISTENING
	listen(sock, 5);

	//THREAD CREATION FOR SERVER INTERACTIVITY
	pthread_t th1;
	int tCount = pthread_create(&th1, NULL,serverThread,NULL);

			
	
	while(true){
		
		
		
		int sfd = accept(sock,(struct sockaddr*)&client,&cSize);

		//EXTRACTING CLIENT IP
		
		strcpy(clientList[clientCount].ip,inet_ntoa(client.sin_addr));
		pipe(clientList[clientCount].pd);
		pipe(clientList[clientCount].pd2);

		
		
		if(sfd<0){	perror("Accepting connection");	exit(1);	}
		


		int pidClient = fork();
		
		if(pidClient == 0){
			//all server-child methods
			serverMethods(sfd,clientList[clientCount].ip);
			exit(0);
			
		}
		else if(pidClient > 0){
			
			//Saving Client Info in list
			clientList[clientCount].port = ntohs(client.sin_port);
			clientList[clientCount].id=clientCount;			
			clientList[clientCount].pid=pidClient;
			strcpy(clientList[clientCount].active,"True");
			
			
			//closing Socket and Pipe ends
			close(sfd);
			close(clientList[clientCount].pd[0]);
			close(clientList[clientCount].pd2[1]);	

			clientCount++;
			

			

		}
			
			

		
	}	
}
