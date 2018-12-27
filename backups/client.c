#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>

void* threadFunc(void *arg){
	int sock = *((int *) arg);
	

	char buff[10000];
	
	while(true){
		int rCount2 = read(sock,buff,sizeof(buff));
		if(rCount2<0){	perror("Reading from Socket Stream");	}

		//if server shuts down
		if(rCount2 == 0){
			write(1,"Server Shut Down. Connection Ended\n",sizeof("Server Shut Down. Connection Ended\n"));
			exit(0);}
		//Disconnect condition
		//if(strcmp(buff,"***")){	write(1,"Disconnecting Socket\n",sizeof("Disconnecting Socket\n"));	break; }

		int wCount3 = write(1,buff,rCount2);
		write(1,"->",2);
		if(wCount3<0){	perror("Writing on screen error");	}

	}
	
}

int main(int argc, char *argv[]){
	

	if(argc<3){	perror("Not enough arguments; Enter IP address and Port");	exit(1);	}

	char buff[10000];

	struct sockaddr_in server;
	struct hostent *host;
 
	//Creating Socket
	int sock = socket(AF_INET,SOCK_STREAM,0);
	if(sock<0){	perror("Opening socket stream");	exit(1);	}

	//Connecting Socket
	server.sin_family = AF_INET;
	host = gethostbyname(argv[1]);
	
	if(host == 0){
		fprintf(stderr, "%s: unknown host\n", argv[1]);
		exit(1);
	}

	bcopy(host->h_addr, &server.sin_addr, host->h_length);

	//converting IP to network
	server.sin_port = htons(atoi(argv[2]));
		
	//Connecting
	int connectCount = connect(sock,(struct sockaddr *) &server,sizeof(server));
	if(connectCount < 0){	perror("Connect Error");	exit(1);	}

	//READING FROM SOCKET FOR THE FIRST TIME
	int readFirst = read(sock,buff,10000);
	write(1,buff,readFirst);
	
	int iCount =1;
	char iBuff[10];
	
	//THREAD CREATION
	pthread_t th1;
	

	/*int *arg= malloc(sizeof(*arg));
	*arg=sock;
	int tCount = pthread_create(&th1, NULL,threadFunc,arg);
	*/
	int tCount = pthread_create(&th1, NULL,threadFunc,(void*) &sock);
	
	

	while(true){
		
		/*int wCount = write(1,"--------------------------------\nEnter a command or write 'help'.\n",66);
		int ipcount = sprintf(iBuff,"%d| ",iCount++);
		write(1,iBuff,ipcount);*/


		int rCount = read(0,buff,sizeof(buff));
		if(rCount<0){	perror("Reading Input. Enter again.\n");	continue;}
		
		
		/*MULTIPLE INSTRUCTION CODE
		
		if(rCount < 10){
			sprintf(buff,"%d %s\n",rCount,iSize);
		}
		else if(rCount > 10){
			sprintf(buff,"%d%s\n",rCount,iSize);
		}
		write(1,buff,strlen(buff));
		//MULTIPLE INSTRUCTION CODE*/



		if(rCount == 5){
			char *token = strtok(buff,"\n");
			if(strcmp(token,"exit")==0||strcmp(token,"disconnect")==0){
				write(1,"Exiting Process\n",sizeof("Exiting Process"));
				exit(0);
			}
		}
		

		int wCount2 = write(sock,buff,rCount);

		if(wCount2<0){	perror("Writing on Socket Stream");	}

		

	}

	close(sock);


}