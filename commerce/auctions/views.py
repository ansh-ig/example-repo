from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing


def index(request):
    activeListings = Listing.objects.filter (isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": allCategories
        })
    else:
        #Get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        price = request.POST["price"]
        category = request.POST["category"]
        #user
        usernow = request.user
        #category content
        category_data = Category.objects.get(categoryName = category)
        #  create a new listing
        newListing = Listing(
            tittle=title,
            description=description,
            imageurl=imageurl,
            price=float(price),
            category=category_data,
            owner = usernow
            )
        #  insert it in our db 
        newListing.save()
        # Redirect to index page
        return HttpResponseRedirect(reverse(index))
    
def displayCategory(request):
    if request.method == "POST":
        formcategory = request.POST['category']
        category = Category.objects.get(categoryName=formcategory)
        activeListings = Listing.objects.filter (isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allCategories
    })

def listing(request, id):
    listingInfo = Listing.objects.get(pk=id)
    isListingInWatchlist = request.user in listingInfo.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": listingInfo,
        "isListingInWatchlist": isListingInWatchlist
    })

def watchlist(request):
    usernow = request.user
    listings = usernow.listingWatchlist.all()
    return render(request, "Auctions/watchlist.html", {
        "listings": listings
    })

def removeWatchlist(request,id):
    listingInfo = Listing.objects.get(pk=id)
    usernow = request.user
    listingInfo.watchlist.remove(usernow)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def addWatchlist(request,id):
    listingInfo = Listing.objects.get(pk=id)
    usernow = request.user
    listingInfo.watchlist.add(usernow)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
